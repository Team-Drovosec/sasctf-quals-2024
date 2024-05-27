import ctypes
from math import ceil

def str_e(self):
    magic = 3257840388504953787
    return ''.join([chr((self[i] ^ (magic & (0xff << ((i % ceil(magic.bit_length() / 8.0)) * 8))) >> ((i % ceil(magic.bit_length() / 8.0)) * 8)) + 1) for i in range(len(self))])


def str_d(self):
    magic = 3257840388504953787
    return ''.join([chr((self[i] - 1) ^ (magic & (0xff << ((i % ceil(magic.bit_length() / 8.0)) * 8))) >> ((i % ceil(magic.bit_length() / 8.0)) * 8)) for i in range(len(self))])


def check_size(a):
    return len(a) == 29 and a[:4] == "SAS{" and a[-1] == "}"

def part2(a):
    b = bytearray(a.sparde.to_bytes(8, 'big'))
    for i in range(len(b)):
        b[i] += b[i] >> 5
    a.sparde = int.from_bytes(b, byteorder="little")


def part3(a):
    b = bytearray(a.spodro.to_bytes(8, 'little'))
    for i in range(len(b)):
        b[i] //= 2
    a.spodro = int.from_bytes(b, byteorder="little")


def code_dumps(f):
    f = f.__code__
    return f'C({f.co_argcount}, {f.co_kwonlyargcount}, {f.co_kwonlyargcount}, {f.co_nlocals}, {f.co_stacksize}, {f.co_flags}, {f.co_code}, {f.co_consts}, {f.co_names}, {f.co_varnames}, \'0\', \'0\', {f.co_firstlineno}, {f.co_lnotab}, {f.co_freevars}, {f.co_cellvars})'


#print(code_dumps(str_d.__code__.co_consts[3]))
for s in ['sparde', 'spodro']:
    print('xD(', str_e(s.encode()).encode('latin-1'), '), ', end='', sep='')

#print(code_dumps(part2))