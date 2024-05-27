#!/usr/bin/env python3
import string
import random

FLAG = "SAS{experienced_wordsearch_enjoyer}".upper()


HEIGHT_START = -64
HEIGHT_END = 100
HEIGHT = HEIGHT_END - HEIGHT_START + 1
WIDTH = HEIGHT
BUILD_LIMIT=32768
SIGN_HEIGHT = 4
SIGN_WIDTH = 10
FILE = "/Users/irdkwmnsb-mac/Library/Application Support/PrismLauncher/instances/1.20.4/.minecraft/saves/New World (2)/datapacks/test/data/minecraft/functions/fill.mcfunction"
ALPHABET = string.ascii_uppercase + string.digits
random.seed(123744)

text_data = [[random.choice(ALPHABET) for _ in range(SIGN_WIDTH * WIDTH)] for _ in range(SIGN_HEIGHT * HEIGHT)]
print(text_data)

print("Total size: ", WIDTH * SIGN_WIDTH, HEIGHT * SIGN_HEIGHT)
START_Y=random.randint(0, HEIGHT * SIGN_HEIGHT - len(FLAG) - 1)
START_X=random.randint(0, WIDTH * SIGN_WIDTH - len(FLAG) - 1)
print("start:", START_X, START_Y)
for i, c in enumerate(FLAG):
    text_data[START_Y + i][START_X + i] = c

print([text_data[START_Y + i][START_X + i] for i in range(len(FLAG))])

print("Start block:", START_Y // SIGN_HEIGHT + HEIGHT_START, START_X // SIGN_WIDTH)

def make_command(X, Y, Z, texts):
    return f"""setblock {X} {Y} {Z} minecraft:oak_wall_sign[facing=west]{{front_text:{{messages:['"{texts[0]}"','"{texts[1]}"','"{texts[2]}"','"{texts[3]}"']}}}}"""

with open("text.txt", "w") as f:
    for line in text_data[::-1]:
        print(*line, sep="", file=f)

with open(FILE, "w") as f:
    print(f"""tellraw @a "filling" """, file=f)

    # for Z in range(0, WIDTH//16):
    #     print(f"forceload 0 {Z}", file = f) # why, dinnerbone?

    # print(f"fill 0 {HEIGHT_START} 0 1 {HEIGHT_END} {WIDTH - 1} minecraft:air replace", file=f)
    
    # for Z in range(0, WIDTH, (WIDTH * HEIGHT * 2) // BUILD_LIMIT):
    #     print(f"fill 0 {HEIGHT_START} 0 1 {HEIGHT_END} {Z} minecraft:air replace", file=f)
    #     print(f"fill 1 {HEIGHT_START} 0 1 {HEIGHT_END} {Z} minecraft:stone replace", file=f)

    for Z in range(WIDTH):
        for Y in range(HEIGHT_START, HEIGHT_END + 1):
            print(f"setblock 0 {Y} {Z} minecraft:air", file=f)
            print(f"setblock 1 {Y} {Z} minecraft:air", file=f)
            print(f"setblock 1 {Y} {Z} minecraft:stone", file=f)
            SIGN_X = Z * SIGN_WIDTH
            SIGN_Y = (Y - HEIGHT_START) * SIGN_HEIGHT
            texts = [''.join(text_data[SIGN_Y + i][SIGN_X : SIGN_X + SIGN_WIDTH]) for i in range(SIGN_HEIGHT - 1, -1, -1)]
            for text in texts:
                if "{" in text:
                    print("!", Y, Z)
            print(make_command(0, Y, Z, texts), file=f)
    
    print(f"""tellraw @a "done" """, file=f)