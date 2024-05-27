from random import randint
import math


def main():
    k = randint(5, 17)
    x = randint(1, math.floor(0xFFFFFFFF / k))
    a = randint(1, k * x)
    b = k * x - a
    print(f"a={a}", f"b={b}", f"k={k}")
    print("".join([hex(i)[2:].zfill(2) for i in x.to_bytes(4, byteorder="little", signed=False)]))


if __name__ == '__main__':
    main()
