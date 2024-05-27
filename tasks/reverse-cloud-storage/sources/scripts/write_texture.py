from PIL import Image


def primes(n: int):
    out = []
    sieve = [True] * (n+1)
    for p in range(2, n+1):
        if (sieve[p]):
            out.append(p)
            for i in range(p, n+1, p):
                sieve[i] = False
    return out


def test_prim_root(root: int, mod: int) -> bool:
    pow_root = root % mod
    power = 1
    while pow_root > 1:
        pow_root = (pow_root * root) % mod
        power += 1
        
    return power == mod - 1


def main():
    data = []
    with open("./internal", "rb") as f:
        f_data = list(f.read())
    data = f_data + list("https://youtu.be/dQw4w9WgXcQ".encode())
    for i in filter(lambda x: x >= len(data), primes(len(data) + 100)):
        for j in [1337]:
            if test_prim_root(j, i):
                p = i
                mod = j

    print("Closest prime", p)
    print("Best mod", mod)
    n = p - 1
    print("Length", n)
    print("Padding", n - len(f_data))
    data = data + [0] * (n - len(data))
    assert len(data) == n, len(data)
    print(f"data[0, {len(f_data) - 1}]")
    idx = [pow(mod, i+1, len(data)+1) - 1 for i in range(len(data))]

    with open("test_encoded", "w") as f:
        test_data = [0] * n
        for k, i in enumerate(idx):
            test_data[i] = data[k]
        print(test_data, file=f)

    with open("test_decoded", "w") as f:
        print(data, file=f)

    with Image.open("../web/assets/gut_orig.png") as img:
        pixels = img.load()
        for k, i in enumerate(idx):
            idx1 = (2 * i) % img.size[0], (2 * i) // img.size[0]
            idx2 = (2 * i + 1) % img.size[0], (2 * i + 1) // img.size[0]
            byte = data[k]
            pixels[idx1] = (
                (pixels[idx1][0] & 0b1111_1100) | (byte & 0b0011),
                (pixels[idx1][1] & 0b1111_1100) | ((byte & 0b1100) >> 2),
                pixels[idx1][2]
            )
            pixels[idx2] = (
                pixels[idx2][0],
                (pixels[idx2][1] & 0b1111_1100) | ((byte & 0b0011_0000) >> 4),
                (pixels[idx2][2] & 0b1111_1100) | ((byte & 0b1100_0000) >> 6),
            )
        img.save("../web/assets/gut.png", subsampling=0, quality=100)

    with Image.open("../web/assets/gut.png") as img:
        pixels = img.load()
        for k, i in enumerate(idx):
            idx1 = (2 * i) % img.size[0], (2 * i) // img.size[0]
            idx2 = (2 * i + 1) % img.size[0], (2 * i + 1) // img.size[0]
            dec = ((pixels[idx1][0] & 0b11) | ((pixels[idx1][1] & 0b11) << 2)) | \
                  (((pixels[idx2][1] & 0b11) << 4) | ((pixels[idx2][2] & 0b11) << 6))
            assert dec == data[k], f"{dec} == {data[k]} [{i}]"


if __name__ == "__main__":
    main()
