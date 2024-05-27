import os
import pathlib
import markovify
import random

texts_paths = list((pathlib.Path(os.path.realpath(__file__)).parent / "processed").glob("*"))
texts = ""
for text_path in texts_paths:
    with open(text_path, "r") as f:
        texts += f.read()


text_model = markovify.NewlineText("\n".join(texts.split(".")))

alphabet = "abcĉdefgĝhĥijĵklmnoprsŝtuŭvz ."

def make_task(seed):
    key = list(alphabet[:-2])
    random.seed(seed)
    random.shuffle(key)
    key = dict(zip(alphabet[:-2], key))
    orig = " ".join([text_model.make_sentence() + "." for _ in range(12)])
    return "".join(key.get(c, c) for c in orig), orig