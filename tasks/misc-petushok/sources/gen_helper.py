import math
import random

if __name__ == "__main__":
    op = "*+^"
    
    body = list()
    for _ in range(128):
        body.append("secret %s= 0x%X"%(random.choice(op),random.getrandbits(256)))
        body.append("secret &= 0x%X"%((1<<256) - 1))
        
    secret = random.getrandbits(256)
    with open("secret.txt","w") as f:
        f.write(str(secret))
    
    for line in body:
        exec(line)

    with open("helper.py","w") as f:
        f.write("def check_secret(secret: int) -> bool:\n")
        for line in body:
            f.write(f"    {line}\n")
        f.write(f"    return secret == {secret}\n")
