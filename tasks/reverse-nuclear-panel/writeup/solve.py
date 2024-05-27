from manticore.core.smtlib import SelectedSolver
from manticore.wasm import ManticoreWASM


def f_arg_gen(buffer_name, buffer_size_bytes):
    def arg_gen(state):
        buffer_size = 8 * buffer_size_bytes
        buf = state.new_symbolic_value(buffer_size, buffer_name)
        state.store.mems[0].write_int(0x100, buf, buffer_size)
        arg = state.new_symbolic_value(32, "check_addr")
        state.constrain(arg == 0x100)
        return [arg]

    return arg_gen


def solve_check(m, f_name, buffer_size_bytes):
    buffer_name = "buffer"
    getattr(m, f_name)(f_arg_gen(buffer_name, buffer_size_bytes))
    for state in m.terminated_states:
        ret = state.platform.stack.pop()
        buf_sym = next(filter(lambda x: x.name == buffer_name, state.input_symbols))
        for res in SelectedSolver.instance().get_all_values(state.constraints, ret):
            if res == 1:
                result = SelectedSolver.instance().get_all_values(state.constraints, buf_sym, 1, True)
                return result[0].to_bytes(buffer_size_bytes, "little", signed=False)


def get_flag(key):
    def arg_gen(state):
        state.store.mems[0].write_int(0x100, int.from_bytes(key, "little", signed=False), len(key) * 8)
        arg = state.new_symbolic_value(32, "check_addr")
        state.constrain(arg == 0x100)
        return [arg]

    m = ManticoreWASM("index.wasm")
    m.perform_hack(arg_gen)
    for st in m.terminated_states:
        flag = st.store.mems[0].read_int(st.platform.stack.pop(), 60 * 8)
        return flag.to_bytes(60, "little").decode()


def main():
    key = b""
    puzzles = [
        ("check1", 8),
        ("check2", 8),
        ("check3", 4),
        ("check4", 4),
        ("check5", 8),
        ("check6", 32),
    ]
    for name, size in puzzles:
        m = ManticoreWASM("index.wasm")
        solution = solve_check(m, name, size)
        key += solution
        print(f"{name}: {solution.hex()}")

    print(f"Full key: {key.hex()}")
    print(f"Flag: {get_flag(key)}")


if __name__ == "__main__":
    main()
