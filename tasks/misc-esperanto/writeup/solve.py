#!/usr/bin/env python3

from typing import Dict, List
import functools
import re
import asyncio


class Solver:
    def __init__(self, words: List[str], alphabet: str, verbose=True):
        self.dictionary = words
        self.known_words = list(filter(lambda x: len(x) >= 2, words))
        self.known_words.sort(key=lambda k: len(k), reverse=True)
        self.alphabet = alphabet
        self.verbose = verbose

    @staticmethod
    def decipher(cyphered: str, key: Dict[str, str]):
        t = ""
        for c in cyphered:
            t += key.get(c) or "_"
        return t

    def solve(self, cyphered: str, start_key=None, depth=0):
        decipher_key = {k: None for k in self.alphabet} | {" ": " ", ".": "."}
        if start_key is not None:
            decipher_key = start_key
        chars_to_find = [k for k, v in decipher_key.items() if v is None]
        # find known phrases
        self.known_words.sort(key=lambda word: sum(1 for c in word if c in decipher_key.values()) - len(word), reverse=False)
        if self.verbose:
            for word in self.known_words[:10]:
                print(word, sum(1 for c in word if c in decipher_key.values()))
        cur_deciphered = self.decipher(cyphered, key=decipher_key)
        for word in self.known_words:
            # if all(c not in word for c in chars_to_find): # we guessed all the letters of this word.
            #     if word == "herba":
            #         print("!", chars_to_find)
            #     continue
            # find where it would fit
            for starts in range(0, len(cyphered) - len(word)):
                for i in range(len(word)):
                    if cur_deciphered[starts + i] == "_":
                        break
                else:
                    continue
                would_make_dkey = dict(decipher_key)
                found_phrase = True
                for i in range(len(word)):
                    if (
                        would_make_dkey[cyphered[starts + i]] is not None
                        and would_make_dkey[cyphered[starts + i]] != word[i]
                    ): # bad symbol
                        found_phrase = False
                        break
                    else:
                        if word[i] in would_make_dkey.values():
                            continue 
                        would_make_dkey[cyphered[starts + i]] = word[i]
                if not found_phrase or would_make_dkey == decipher_key:
                    continue
                else:
                    d = self.decipher(cyphered, would_make_dkey)
                    all_words_exist = True
                    for check_word in d.split(" "):
                        if not any(
                            re.match(check_word.rstrip(".").replace("_", "."), dict_word)
                            for dict_word in self.dictionary
                        ):
                            all_words_exist = False
                    if not all_words_exist:
                        continue
                    if self.verbose:
                        print("=" * (depth), depth)
                        print(f"Found {word}, new key: {would_make_dkey}")
                        print(f"Deciphered: {d}")
                    if "_" not in d:
                        return d
                    result = self.solve(cyphered, start_key=would_make_dkey, depth=depth + 1)
                    if result:
                        return result
        return None

async def solve(host, port, solver: Solver):
    reader, writer = await asyncio.open_connection(host, port)
    line = await reader.readline()
    print(line)
    while True:
        solved_line = await reader.readline()
        print(solved_line)
        task = (await reader.readline()).decode().strip()
        result = solver.solve(task)
        print("solved:", result)
        writer.write(result.encode() + b'\n')
        print(await reader.readline())

if __name__ == "__main__":
    with open("words") as f:
        words = f.read().split()
    solver = Solver(words, "abcĉdefgĝhĥijĵklmnoprsŝtuŭvz .", verbose=True)
    asyncio.run(solve("localhost", 13337, solver))
