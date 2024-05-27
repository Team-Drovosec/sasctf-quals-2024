from random import randint, randbytes


def main():
    # (ax + b)c + d == e
    data_a = [randint(2, 32) for _ in range(4)]
    data_b = [randint(10**3, 10**5) for _ in range(4)]
    data_c = [randint(2, 32) for _ in range(4)]
    data_d = [randint(10**3, 10**5) for _ in range(4)]
    data_e = []
    data = randbytes(8)
    data_short = [int.from_bytes(data[i:i+2], byteorder="little", signed=False) for i in range(0, 8, 2)]
    for i in range(len(data_short)):
        data_e.append((data_a[i]*data_short[i] + data_b[i]) * data_c[i] + data_d[i])

    print("A=", data_a)
    print("B=", data_b)
    print("C=", data_c)
    print("D=", data_d)
    print("E=", data_e)

    print("X=", "".join([hex(i)[2:].zfill(2) for i in data]))


if __name__ == '__main__':
    main()
