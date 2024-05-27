def fib(n):
    a = 0
    b = 1

    if n == 0:
        return a
    elif n == 1:
        return b
    else:
        for _ in range(2, n + 1):
            c = a + b
            a = b
            b = c
        return b


def main():
    result = fib(46)  # 2971215073
    print([i for i in result.to_bytes(4, 'little', signed=False)])
    print(''.join([hex(i)[2:].zfill(2) for i in result.to_bytes(4, 'little', signed=False)]))


if __name__ == '__main__':
    main()
