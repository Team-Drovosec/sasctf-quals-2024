#![allow(non_snake_case)]

use std::collections::{HashMap, HashSet};
use std::{fmt, vec};

use dioxus::prelude::*;
use tracing::Level;
use web_sys::wasm_bindgen::{JsCast, JsValue};
use async_trait::async_trait;

const _BULMA_URL: &str = manganis::mg!(file("https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css"));
const _MAINCSS_URL: &str = manganis::mg!(file("assets/main.css"));

#[cfg(feature = "server")]
use tower_sessions::{Expiry, MemoryStore, SessionManagerLayer};

const SESSION_KEY: &str = "session";

#[derive(Default, serde::Deserialize, serde::Serialize, Clone)]
struct UserSession {
    safe_programs: HashSet<[u8;32]>,
    is_admin: bool,
}

fn main() {
    dioxus_logger::init(Level::ERROR).expect("failed to init logger");
    #[cfg(feature = "web")]
    {
        launch(App);
    }
    #[cfg(feature = "server")]
    {
        use axum::routing::*;
        tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(async move {
            let session_store = MemoryStore::default();
            let session_layer = SessionManagerLayer::new(session_store)
                .with_secure(false);
        
            let app = Router::new()
                .serve_dioxus_application(ServeConfig::builder().build(), || {
                    VirtualDom::new(App)
                })
                .await
                .layer(session_layer);
            let addr = std::net::SocketAddr::from(([0, 0, 0, 0], 80));
            let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();

            axum::serve(listener, app.into_make_service())
                .await
                .unwrap();
        });
    }
}

mod Executor {
    use std::collections::HashSet;
    use sha3::{Digest, Sha3_256};

    #[derive(Clone, Copy, PartialEq, Debug, serde::Serialize, serde::Deserialize)]
    pub(crate) enum Reg {
        R0,
        R1
    }

    #[derive(Clone, PartialEq, Debug, serde::Serialize, serde::Deserialize)]
    pub(crate) enum Instruction {
        IncPtr { ptr: Reg },
        MovPtrConst { ptr: Reg, value: u8 },
        WhileNZLoop { ptr: Reg, instructions: Vec<Instruction> },
        IncPtrValue { ptr: Reg },
        XorPtrs { ptr_dst: Reg, ptr_src: Reg, length: u8 },
        PutBlobPtr { ptr: Reg, data: Vec<u8> },
        ReadValuePtr {ptr: Reg, length: u8 },
        PrintValuePtr { ptr: Reg, length: u8 },
        WriteFlagPtr { ptr: Reg },
    }

    struct ExecState {
        memory: [u8; 256],
        r0_ptr: u8,
        r1_ptr: u8,

        step: u32,
    }

    fn execute(state: &mut ExecState, instructions: &Vec<Instruction>, input: &mut Vec<u8>, max_steps: u32) -> Result<Vec<u8>, String> {
        fn read_reg_data(state: &ExecState, reg: &Reg) -> u8 {
            state.memory[read_reg(state, reg) as usize]
        }
        fn read_reg(state: &ExecState, reg: &Reg) -> u8 {
            match reg {
                Reg::R0 => state.r0_ptr,
                Reg::R1 => state.r1_ptr,
            }
        }
        let mut output = Vec::<u8>::new();
        for inst in instructions.iter() {
            match inst {
                Instruction::WhileNZLoop { ptr, instructions } => {
                    if instructions.len() < 256 {
                        while read_reg_data(&state, ptr) != 0 {
                            match execute(state, instructions, input, max_steps) {
                                Err(err) => return Err(err),
                                Ok(out) => output.extend(out),
                            }
                        }
                    } else {
                        return Err("💁‍♂️ 🌅".to_string());
                    }
                },
                Instruction::MovPtrConst { ptr, value } => {
                    *match ptr {
                        Reg::R0 => &mut state.r0_ptr,
                        Reg::R1 => &mut state.r1_ptr,
                    } = *value;
                },
                Instruction::IncPtr { ptr } => {
                    match ptr {
                        Reg::R0 => state.r0_ptr = state.r0_ptr.wrapping_add(1),
                        Reg::R1 => state.r1_ptr = state.r1_ptr.wrapping_add(1),
                    };
                },
                Instruction::IncPtrValue { ptr } => {
                    state.memory[read_reg_data(&state, ptr) as usize] = state.memory[read_reg_data(&state, ptr) as usize].wrapping_add(1);
                },
                Instruction::XorPtrs { ptr_dst, ptr_src, length } => {
                    let dst = read_reg(&state, ptr_dst) as usize;
                    let src = read_reg(&state, ptr_src) as usize;
                    for i in 0..(*length as usize) {
                        state.memory[(dst + i) % 256] ^= state.memory[(src + i) % 256];
                    }
                },
                Instruction::PutBlobPtr { ptr, data } => {
                    if data.len() < 256 {
                        let dst = read_reg(&state, ptr) as usize;
                        for i in 0..data.len() {
                            state.memory[(dst + i) % 256] = data[i];
                        } 
                    } else {
                        return Err("💁‍♂️ 🌅".to_string());
                    }
                },
                Instruction::ReadValuePtr { ptr, length } => {
                    let dst = read_reg(&state, ptr) as usize;
                    for i in 0..(*length as usize) {
                        state.memory[(dst + i) % 256] = if let Some(byte) = input.pop() {byte} else {return Err("💪 🚫 ✍ 🔢".to_string());};
                    }
                },
                Instruction::PrintValuePtr { ptr, length } => {
                    let dst = read_reg(&state, ptr) as usize;
                    for i in 0..(*length as usize) {
                        output.push(state.memory[(dst + i) % 256]);
                    }
                },
                Instruction::WriteFlagPtr { ptr } => {
                    let dst = read_reg(&state, ptr) as usize;
                    let flag = std::env::var("FLAG").unwrap();
                    for i in 0..flag.len() {
                        state.memory[(dst + i) % 256] = flag.as_bytes()[i];
                    }
                },
            }
            state.step += 1;
            if state.step == max_steps {
                return Err("👅 📊".to_string());
            }
        }
        Ok(output)
    }

    fn is_privileged_program(program: &Vec<Instruction>) -> bool {
        for instruction in program.iter() {
            if let Instruction::WhileNZLoop { instructions, .. } = instruction {
                if is_privileged_program(instructions) {
                    return true;
                }
            } else if let Instruction::WriteFlagPtr { ptr: _ } = instruction {
                return true;
            }
        }
        false
    }

    pub(crate) fn run_program(program: &Vec<Instruction>, mut input: Vec<u8>, safe_programs: &mut HashSet<[u8;32]>, is_admin: bool) -> String {
        let program_hash: [u8;32] = {
            let mut hasher = Sha3_256::new();
            program_hash(program, &mut hasher);
            hasher.finalize().into()
        };
        if safe_programs.contains(&program_hash) || !is_privileged_program(program) || is_admin {
            safe_programs.insert(program_hash);
            let mut state = ExecState { memory: [0; 256], r0_ptr: 0, r1_ptr: 0, step: 0 };
            input.reverse();
            match execute(&mut state, program, &mut input, 256) {
                Ok(output) => format!("{:?}", output),
                Err(err) => err,
            }
        } else {
            "👆 🚫 😌 🏃 👉 📋".to_string()
        }
    }

    fn program_hash<T: sha3::Digest>(program: &Vec<Instruction>, hasher: &mut T) {
        fn hash_reg<T: sha3::Digest>(reg: &Reg, hasher: &mut T) {
            match reg {
                Reg::R0 => hasher.update(b"\x00"),
                Reg::R1 => hasher.update(b"\x01"),
            }
        }

        for instruction in program.iter() {
            match instruction {
                Instruction::IncPtr { ptr } => {
                    hasher.update(b"\x00");
                    hash_reg(ptr, hasher);
                },
                Instruction::MovPtrConst { ptr, value } => {
                    hasher.update(b"\x01");
                    hash_reg(ptr, hasher);
                    hasher.update(value.to_le_bytes());
                },
                Instruction::WhileNZLoop { ptr, instructions } => {
                    hasher.update(b"\x02");
                    hash_reg(ptr, hasher);
                    program_hash(instructions, hasher);
                    hasher.update(instructions.len().to_le_bytes());
                },
                Instruction::IncPtrValue { ptr } => {
                    hasher.update(b"\x03");
                    hash_reg(ptr, hasher);
                },
                Instruction::XorPtrs { ptr_dst, ptr_src, length } => {
                    hasher.update(b"\x04");
                    hash_reg(ptr_dst, hasher);
                    hash_reg(ptr_src, hasher);
                    hasher.update(length.to_le_bytes());
                },
                Instruction::PutBlobPtr { ptr, data } => {
                    hasher.update(b"\x05");
                    hash_reg(ptr, hasher);
                    hasher.update(data);
                    hasher.update(data.len().to_le_bytes());
                },
                Instruction::ReadValuePtr { ptr, length } => {
                    hasher.update(b"\x06");
                    hash_reg(ptr, hasher);
                    hasher.update(length.to_le_bytes());
                },
                Instruction::PrintValuePtr { ptr, length } => {
                    hasher.update(b"\x07");
                    hash_reg(ptr, hasher);
                    hasher.update(length.to_le_bytes());
                },
                Instruction::WriteFlagPtr { ptr } => {
                    hasher.update(b"\x08");
                    hash_reg(ptr, hasher);
                },
            }
        }
    }
}

use Executor::Reg;

impl fmt::Display for Reg {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", match self {
            Reg::R0 => "R0",
            Reg::R1 => "R1",
        })
    }
}

#[derive(Clone, PartialEq, Debug)]
enum Instruction {
    IncPtr { ptr: Reg },
    MovPtrConst { ptr: Reg, value: Option<u8> },
    WhileNZLoop { ptr: Reg, list_id: u32 },
    IncPtrValue { ptr: Reg },
    XorPtrs { ptr_dst: Reg, ptr_src: Reg, length: Option<u8> },
    PutBlobPtr { ptr: Reg, data: Option<Vec<u8>> },
    ReadValuePtr {ptr: Reg, length: Option<u8> },
    PrintValuePtr { ptr: Reg, length: Option<u8> },
    WriteFlagPtr { ptr: Reg },
}

struct ObjectsState<T> {
    data: HashMap::<u32, T>,
    next_id: u32,
}

impl<T> ObjectsState<T> {
    fn new() -> Self {
        Self { data: HashMap::new(), next_id: 0 }
    }

    fn add(&mut self, instruction: T) -> u32 {
        let id = self.next_id;
        self.next_id += 1;
        self.data.insert(id, instruction);
        id
    }
    fn get(&self, id: u32) -> &T {
        self.data.get(&id).unwrap()
    }
    fn get_mut(&mut self, id: u32) -> &mut T {
        self.data.get_mut(&id).unwrap()
    }
    fn remove(&mut self, id: u32) {
        self.data.remove(&id).unwrap();
    }
}

#[component]
fn InstructionDragTemplate(send_name: String, name: String) -> Element {
    rsx!(
        a {
            class: "panel-block",
            draggable: true,
            ondragstart: move |event| {
                let ev = event.downcast::<web_sys::MouseEvent>().unwrap().dyn_ref::<web_sys::DragEvent>().unwrap();
                ev.data_transfer().unwrap().set_data("instruction/new", &send_name).unwrap();
            },
            "{name}"
        }
    )
}

#[component]
fn InstructionBox(
    name: String, op1: Element, op2: Element, op3: Element, rem: Element,
    instructions: Signal<ObjectsState<Instruction>>,
    instruction_ids: Signal<ObjectsState<Vec<u32>>>,
    list_id: u32,
    instruction_id: u32
) -> Element {
    rsx!(
        div {
            class: "box",
            div {
                class: "columns is-vcentered",
                div {
                    class: "column is-2",
                    "{name}"
                }
                
                div {
                    class: "column is-2",
                    {op1}
                }
                div {
                    class: "column is-4",
                    {op2}
                }
                div {
                    class: "column is-3",
                    {op3}
                }
                div {
                    class: "column is-1 is-right",
                    button {
                        class: "button is-danger",
                        onclick: move |_| {
                            // fn remove_recursive(instruction_id: u32, mut instructions: Signal<ObjectsState<Instruction>>, mut instruction_ids: Signal<ObjectsState<Vec<u32>>>) {
                            //     let mut insts_to_remove: Vec<u32> = vec![];
                            //     if let Instruction::WhileNZLoop(while_loop) = instructions.read().get(instruction_id) {
                            //         for inst_id in instruction_ids.read().get(while_loop.list_id) {
                            //             insts_to_remove.push(*inst_id);
                            //         }
                            //         instruction_ids.write().remove(while_loop.list_id);
                            //     }
                            //     for inst_id in insts_to_remove.iter() {
                            //         remove_recursive(*inst_id, instructions, instruction_ids);
                            //     }
                            //     instructions.write().remove(instruction_id);
                            // }
                            // remove_recursive(instruction_id, instructions, instruction_ids);
                            instruction_ids.write().get_mut(list_id).retain(|x| *x != instruction_id);
                        },
                        "X"
                    }
                }
            }
            {rem}
        }
    )
}

fn str_to_reg(value: &str) -> Reg {
    match value {
        "[R0]" => Reg::R0,
        "[R1]" => Reg::R1,
        _ => panic!("err"),
    }
}

#[component]
fn InstructionList(
    instructions: Signal<ObjectsState<Instruction>>,
    list_id: u32,
    instruction_ids: Signal<ObjectsState<Vec<u32>>>,
    borders: Signal<Vec<bool>>
) -> Element {
    use_effect(move || {
        let new_len = instruction_ids.read().get(list_id).len() + 1;
        if borders().len() != new_len {
            borders.write().resize(new_len, false);
        }
    });
    fn is_bottom_part(elem: &web_sys::Element, mouse_y: i32) -> bool {
        let elem_rect = elem.get_bounding_client_rect();
        elem_rect.bottom() - (mouse_y as f64) <= (elem_rect.bottom() - elem_rect.top()) / 2f64
    }
    let mut set_borders = move |index: usize, top: bool, bottom: bool| {
        let mut borders = borders.write();
        borders[index] = top;
        borders[index+1] = bottom;
    };
    fn convert_to_dragevent(event: &dioxus::events::DragEvent)-> &web_sys::DragEvent {
        event.downcast::<web_sys::MouseEvent>().unwrap().dyn_ref::<web_sys::DragEvent>().unwrap()
    }
    let mut process_instruction_new = move |ev: &web_sys::DragEvent, mut new_index: usize| {
        ev.prevent_default();
        let text = ev.data_transfer().unwrap().get_data("instruction/new").unwrap();
        if text.len() > 0 {
            let new_id = instructions.write().add(
                match text.as_str() {
                    "inc" => Instruction::IncPtr{ ptr: Reg::R0 },
                    "mov" => Instruction::MovPtrConst {ptr: Reg::R0, value: Some(0u8)},
                    "while" => Instruction::WhileNZLoop{ ptr: Reg::R0, list_id: instruction_ids.write().add(vec![]) },
                    "incval" => Instruction::IncPtrValue{ ptr: Reg::R0 },
                    "xor" => Instruction::XorPtrs { ptr_dst: Reg::R0, ptr_src: Reg::R1, length: Some(0u8) },
                    "put" => Instruction::PutBlobPtr { ptr: Reg::R0, data: Some(Vec::new()) },
                    "read" => Instruction::ReadValuePtr { ptr: Reg::R0, length: Some(0u8) },
                    "print" => Instruction::PrintValuePtr { ptr: Reg::R0, length: Some(0u8) },
                    "flag" => Instruction::WriteFlagPtr { ptr: Reg::R0 },
                    _ => panic!("unknown instruction"),
                }
            );
            instruction_ids.write().get_mut(list_id).insert(new_index, new_id);
        }
        let text = ev.data_transfer().unwrap().get_data("instruction/move").unwrap();
        if text.len() > 0 {
            let parts: Vec<u32> = text.split("_").map(|sub| sub.parse::<u32>().unwrap()).collect();
            // Check that we are not moving instruction into itself
            fn check(from_instr_id: u32, to_list_id: u32, instructions: &ObjectsState<Instruction>, instruction_ids: &ObjectsState<Vec<u32>>) -> bool {
                if let Instruction::WhileNZLoop {list_id,..} = instructions.get(from_instr_id) {
                    if *list_id == to_list_id {
                        return false;
                    } else {
                        let array = instruction_ids.get(*list_id);
                        for instr_id in array {
                            if !check(*instr_id, to_list_id, instructions, instruction_ids) {
                                return false;
                            }
                        }
                    }
                }
                return true;
            }
            if check(parts[1], list_id, &instructions.read(), &instruction_ids.read()) {
                let mut instr_ids = instruction_ids.write();
                if list_id == parts[0] {
                    let index = instr_ids.get(list_id).iter().position(|x| *x == parts[1]).unwrap();
                    if new_index > index {
                        new_index -= 1;
                    }
                }
                instr_ids.get_mut(parts[0]).retain(|x| *x != parts[1]);
                instr_ids.get_mut(list_id).insert(new_index, parts[1]);
            }
        }
    };
    let mut elem_border = use_signal(move || false);
    rsx!(
        ul {
            class: if borders.read().len() == 1 {"menu-list py-4"} else {"menu-list"},
            style: if elem_border() {"background-color: cyan;"} else {"background-color: transparent;"},
            ondragover: move |event| {
                if borders.read().len() == 1 {
                    event.stop_propagation();
                    let ev = convert_to_dragevent(&event);
                    if ev.data_transfer().unwrap().types().includes(&JsValue::from_str("instruction/new"), 0) || 
                       ev.data_transfer().unwrap().types().includes(&JsValue::from_str("instruction/move"), 0) {
                        ev.prevent_default();
                        *elem_border.write() = true;
                    }
                }
            },
            ondragleave: move |event| {
                if borders.read().len() == 1 {
                    event.stop_propagation();
                    *elem_border.write() = false;
                }
            },
            ondrop: move |event| {
                if borders.read().len() == 1 {
                    event.stop_propagation();
                    *elem_border.write() = false;
                    let ev = convert_to_dragevent(&event);
                    ev.prevent_default();
                    process_instruction_new(ev, 0);
                }
            },
            hr{
                class: "instruction-separator",
                style: if borders.read()[0] {"background-color: cyan;"} else {"background-color: transparent;"}
            }
            for (index, (instruction_id, border)) in instruction_ids.read().get(list_id).iter().zip(borders.read().iter().skip(1)).enumerate() {
                {
                    let instruction_id = *instruction_id;
                    let get_real_current_target = move || web_sys::window().unwrap().document().unwrap().get_element_by_id(&format!("li-{}", instruction_id)).unwrap();
                    rsx!(
                        li {
                            id: "li-{instruction_id}",
                            key: "{instruction_id}",
                            draggable: true,
                            ondragstart: move |event| {
                                event.stop_propagation();
                                let ev = event.downcast::<web_sys::MouseEvent>().unwrap().dyn_ref::<web_sys::DragEvent>().unwrap();
                                ev.data_transfer().unwrap().set_data("instruction/move", &format!("{}_{}", list_id, instruction_id)).unwrap();
                            },
                            ondragover: move |event| {
                                event.stop_propagation();
                                let ev = convert_to_dragevent(&event);
                                if ev.data_transfer().unwrap().types().includes(&JsValue::from_str("instruction/new"), 0) ||
                                   ev.data_transfer().unwrap().types().includes(&JsValue::from_str("instruction/move"), 0) {
                                    let elem = ev.target().unwrap().dyn_into::<web_sys::Element>().unwrap();
                                    if elem.tag_name() != "HR" {
                                        ev.prevent_default();
                                        if is_bottom_part(&get_real_current_target(), ev.client_y()) {
                                            set_borders(index, false, true);
                                        } else {
                                            set_borders(index, true, false);
                                        }
                                    }
                                }
                            },
                            ondragleave: move |event| {
                                event.stop_propagation();
                                set_borders(index, false, false);
                            },
                            ondrop: move |event| {
                                event.stop_propagation();
                                set_borders(index, false, false);
                                let ev = convert_to_dragevent(&event);
                                process_instruction_new(ev, if is_bottom_part(&get_real_current_target(), ev.client_y()) {index+1} else {index});
                            },
                            match instructions.read().get(instruction_id) {
                                Instruction::IncPtr { ptr } => rsx!(InstructionBox {
                                    name: "📈",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::IncPtr {ptr} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(""),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::MovPtrConst { ptr, value } => rsx!(InstructionBox {
                                    name: "⤵",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::MovPtrConst {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(input {
                                        class: if value.is_some() {"input"} else {"input is-danger"},
                                        r#type: "number",
                                        value: num_to_string(value),
                                        min: 0,
                                        max: 255,
                                        onchange: move |event| {
                                            if let Instruction::MovPtrConst {value, ..} = instructions.write().get_mut(instruction_id) {
                                                if let Ok(num) = event.value().parse::<u8>() {
                                                    *value = Some(num);
                                                } else {
                                                    *value = None;
                                                }
                                            } else {
                                                panic!("err")
                                            }
                                        }
                                    }),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::WhileNZLoop {ptr, list_id: inner_list_id} => {
                                    let borders = use_signal(move || vec![false; instruction_ids.read().get(*inner_list_id).len()+1]);
                                    rsx!(InstructionBox {
                                        name: "⏪➰",
                                        op1: rsx!(div {
                                            class: "select",
                                            select {
                                                onchange: move |event| {
                                                    if let Instruction::WhileNZLoop {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                        *ptr = str_to_reg(event.value().as_str());
                                                    } else {
                                                        panic!("err")
                                                    }
                                                },
                                                option {
                                                    selected: *ptr == Reg::R0,
                                                    "[R0]"
                                                }
                                                option {
                                                    selected: *ptr == Reg::R1,
                                                    "[R1]"
                                                }
                                            }
                                        }),
                                        op2: rsx!(""),
                                        op3: rsx!(""),
                                        rem: rsx!(InstructionList {instructions, instruction_ids, list_id: *inner_list_id, borders}),
                                        instruction_ids,
                                        instructions,
                                        list_id,
                                        instruction_id,
                                    })
                                },
                                Instruction::IncPtrValue { ptr } => rsx!(InstructionBox {
                                    name: "📈💲",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::IncPtrValue {ptr} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(""),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::XorPtrs { ptr_dst, ptr_src, length } => rsx!(InstructionBox {
                                    name: "🌟⚖️",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::XorPtrs {ptr_dst, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr_dst = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr_dst == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr_dst == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::XorPtrs {ptr_src, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr_src = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr_src == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr_src == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op3: rsx!(input {
                                        class: if length.is_some() {"input"} else {"input is-danger"},
                                        r#type: "number",
                                        value: num_to_string(length),
                                        min: 0,
                                        max: 255,
                                        onchange: move |event| {
                                            if let Instruction::XorPtrs {length, ..} = instructions.write().get_mut(instruction_id) {
                                                if let Ok(num) = event.value().parse::<u8>() {
                                                    *length = Some(num);
                                                } else {
                                                    *length = None;
                                                }
                                            } else {
                                                panic!("err")
                                            }
                                        }
                                    }),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::PutBlobPtr { ptr, data } => rsx!(InstructionBox {
                                    name: "🚮",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::PutBlobPtr {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(input {
                                        class: if data.is_some() {"input"} else {"input is-danger"},
                                        value: blob_to_string(data),
                                        onchange: move |event| {
                                            if let Instruction::PutBlobPtr {data, ..} = instructions.write().get_mut(instruction_id) {
                                                *data = parse_blob(event.value());
                                            } else {
                                                panic!("err")
                                            }
                                        }
                                    }),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::ReadValuePtr { ptr, length } => rsx!(InstructionBox {
                                    name: "✍",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::ReadValuePtr {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(input {
                                        class: if length.is_some() {"input"} else {"input is-danger"},
                                        r#type: "number",
                                        value: num_to_string(length),
                                        min: 0,
                                        max: 255,
                                        onchange: move |event| {
                                            if let Instruction::ReadValuePtr {length, ..} = instructions.write().get_mut(instruction_id) {
                                                if let Ok(num) = event.value().parse::<u8>() {
                                                    *length = Some(num);
                                                } else {
                                                    *length = None;
                                                }
                                            } else {
                                                panic!("err")
                                            }
                                        }
                                    }),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::PrintValuePtr { ptr, length } => rsx!(InstructionBox {
                                    name: "🖨",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::PrintValuePtr {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(input {
                                        class: if length.is_some() {"input"} else {"input is-danger"},
                                        r#type: "number",
                                        value: num_to_string(length),
                                        min: 0,
                                        max: 255,
                                        onchange: move |event| {
                                            if let Instruction::PrintValuePtr {length, ..} = instructions.write().get_mut(instruction_id) {
                                                if let Ok(num) = event.value().parse::<u8>() {
                                                    *length = Some(num);
                                                } else {
                                                    *length = None;
                                                }
                                            } else {
                                                panic!("err")
                                            }
                                        }
                                    }),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                                Instruction::WriteFlagPtr { ptr } => rsx!(InstructionBox {
                                    name: "🏴",
                                    op1: rsx!(div {
                                        class: "select",
                                        select {
                                            onchange: move |event| {
                                                if let Instruction::WriteFlagPtr {ptr, ..} = instructions.write().get_mut(instruction_id) {
                                                    *ptr = str_to_reg(event.value().as_str());
                                                } else {
                                                    panic!("err")
                                                }
                                            },
                                            option {
                                                selected: *ptr == Reg::R0,
                                                "[R0]"
                                            }
                                            option {
                                                selected: *ptr == Reg::R1,
                                                "[R1]"
                                            }
                                        }
                                    }),
                                    op2: rsx!(""),
                                    op3: rsx!(""),
                                    rem: rsx!(""),
                                    instruction_ids,
                                    instructions,
                                    list_id,
                                    instruction_id,
                                }),
                            }
                        }
                        hr {
                            class: "instruction-separator",
                            style: if *border {"background-color: cyan;"} else {"background-color: transparent;"}
                        }
                    )
                }
            }
        }
    )
}

fn parse_blob(data: String) -> Option<Vec<u8>> {
    if data.len() != 0 {
        let parsed = data.split_whitespace().map(|part| part.parse::<u8>());
        if parsed.clone().all(|parsed| parsed.is_ok()) {
            Some(parsed.map(|parsed| parsed.unwrap()).collect())
        } else {
            None
        }
    } else {
        Some(vec![])
    }
}

fn blob_to_string(blob: &Option<Vec<u8>>) -> String {
    if let Some(data) = blob {
        data.iter().map(|x| x.to_string()).collect::<Vec::<String>>().join(" ").to_string()
    } else {
        "".to_string()
    }
}

fn num_to_string(num: &Option<u8>) -> String {
    if let Some(data) = num {
        data.to_string()
    } else {
        "".to_string()
    }
}

#[component]
fn App() -> Element {
    let mut program_input = use_signal(|| Some(vec![72u8, 101u8, 108u8, 108u8, 111u8, 32u8, 87u8, 111u8, 114u8, 108u8, 100u8, 33u8]));
    let mut program_output = use_signal(|| String::from(""));
    let instructions = use_signal(|| {
        let mut state = ObjectsState::<Instruction>::new();
        state.add(Instruction::MovPtrConst { ptr: Reg::R0, value: Some(17u8) });
        state.add(Instruction::MovPtrConst { ptr: Reg::R1, value: Some(57u8) });
        state.add(Instruction::WhileNZLoop { ptr: Reg::R0, list_id: 1u32 });
        state
    });

    let instruction_ids = use_signal(|| {
        let mut state = ObjectsState::<Vec<u32>>::new();
        state.add(vec![0, 2]);
        state.add(vec![1]);
        state
    });
    let borders = use_signal(|| vec![false, false, false]);

    rsx! {
        section {
            class: "hero",
            div {
                class: "hero-body",
                p {
                    class: "title",
                    "🏁 🇪🇸"
                }
            }
        }
        div {
            class: "container",
            div {
                class: "columns",
                div {
                    class: "column",
                    div {
                        class: "menu",
                        InstructionList {instructions, instruction_ids, list_id: 0u32, borders}
                    }
                    input {
                        class: if program_input().is_none() {"input has-fixed-size is-danger"} else {"input has-fixed-size"},
                        placeholder: "🔢",
                        value: "{blob_to_string(&program_input())}",
                        onchange: move |event| {
                            program_input.set(parse_blob(event.value()));
                        }
                    }
                    div {
                        class: "buttons is-right mt-2",
                        button {
                            class: "button is-primary",
                            onclick: move |_| async move {
                                fn convert_inst_list(list_id: u32, instructions: &ObjectsState<Instruction>, instruction_ids: &ObjectsState<Vec<u32>>) -> Option<Vec<Executor::Instruction>> {
                                    let mut result = Vec::<Executor::Instruction>::new();
                                    for inst_id in instruction_ids.get(list_id).iter() {
                                        result.push(match instructions.get(*inst_id) {
                                            Instruction::WhileNZLoop { ptr, list_id: inner_list_id } => {
                                                if let Some(inner_instructions) = convert_inst_list(*inner_list_id, instructions, instruction_ids) {
                                                    Executor::Instruction::WhileNZLoop { ptr: *ptr, instructions: inner_instructions }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::MovPtrConst { ptr, value } => {
                                                if let Some(value) = value {
                                                    Executor::Instruction::MovPtrConst { ptr: *ptr, value: *value }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::IncPtr { ptr } => {
                                                Executor::Instruction::IncPtr { ptr: *ptr }
                                            },
                                            Instruction::IncPtrValue { ptr } => {
                                                Executor::Instruction::IncPtrValue { ptr: *ptr }
                                            },
                                            Instruction::XorPtrs { ptr_dst, ptr_src, length } => {
                                                if let Some(length) = length {
                                                    Executor::Instruction::XorPtrs { ptr_dst: *ptr_dst, ptr_src: *ptr_src, length: *length }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::PutBlobPtr { ptr, data } => {
                                                if let Some(data) = data {
                                                    Executor::Instruction::PutBlobPtr { ptr: *ptr, data: data.clone() }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::ReadValuePtr { ptr, length } => {
                                                if let Some(length) = length {
                                                    Executor::Instruction::ReadValuePtr { ptr: *ptr, length: *length }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::PrintValuePtr { ptr, length } => {
                                                if let Some(length) = length {
                                                    Executor::Instruction::PrintValuePtr { ptr: *ptr, length: *length }
                                                } else {
                                                    return None;
                                                }
                                            },
                                            Instruction::WriteFlagPtr { ptr } => {
                                                Executor::Instruction::WriteFlagPtr { ptr: *ptr }
                                            },
                                        });
                                    }
                                    Some(result)
                                }
                                if let Some(input) = program_input() {
                                    if let Some(program) = convert_inst_list(0, &instructions.read(), &instruction_ids.read()) {
                                        if let Ok(data) = execute_program(program, input).await {
                                            program_output.set(data.clone());
                                        }
                                    }
                                } else {
                                    program_output.set("🔧 🌐 ❌".to_string());
                                }
                            },
                            "🛠"
                        }
                    }
                    textarea {
                        class: "textarea has-fixed-size",
                        placeholder: "🏁 🛠",
                        readonly: true,
                        dangerous_inner_html: "{program_output}"
                    }
                }
                div {
                    class: "column is-one-quarter",
                    nav {
                        class: "panel",
                        InstructionDragTemplate {send_name: "inc", name: "📈"}
                        InstructionDragTemplate {send_name: "mov", name: "⤵"}
                        InstructionDragTemplate {send_name: "while", name: "⏪➰"}
                        InstructionDragTemplate {send_name: "incval", name: "📈💲"}
                        InstructionDragTemplate {send_name: "xor", name: "🌟⚖️"}
                        InstructionDragTemplate {send_name: "put", name: "🚮"}
                        InstructionDragTemplate {send_name: "read", name: "✍"}
                        InstructionDragTemplate {send_name: "print", name: "🖨"}
                        InstructionDragTemplate {send_name: "flag", name: "🏴"}
                    }
                }
            } 
        }
    }
}

#[cfg(feature = "server")]
pub struct MySession(
    pub tower_sessions::Session,
);
#[cfg(feature = "server")]
impl std::ops::Deref for MySession {
    type Target = tower_sessions::Session;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
#[cfg(feature = "server")]
impl std::ops::DerefMut for MySession {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

#[cfg(feature = "server")]
#[async_trait]
impl<S: std::marker::Sync + std::marker::Send> axum::extract::FromRequestParts<S> for MySession {
    type Rejection = std::convert::Infallible;

    async fn from_request_parts(
        parts: &mut axum::http::request::Parts,
        state: &S,
    ) -> Result<Self, Self::Rejection> {
        Ok(tower_sessions::Session::from_request_parts(parts, state)
        .await
        .map(MySession)
        .unwrap())
    }
}

use server_fn::codec::Cbor;

#[server(ExecuteProgram, input=Cbor, output=Cbor)]
async fn execute_program(program: Vec<Executor::Instruction>, input: Vec<u8>) -> Result<String, ServerFnError> {
    let session: MySession = extract().await.unwrap();
    let mut user_session: UserSession = session.get(SESSION_KEY).await.unwrap().unwrap_or_default();
    let result = Executor::run_program(&program, input, &mut user_session.safe_programs, user_session.is_admin);
    session.insert(SESSION_KEY, user_session.clone()).await.unwrap();
    Ok(result)
}

#[server]
async fn get_server_data() -> Result<String, ServerFnError> {
    Ok("a".to_string())
}
