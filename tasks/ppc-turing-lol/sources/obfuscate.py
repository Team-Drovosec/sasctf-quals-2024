import random
import itertools

random.seed(42)


alphabet = ["A", "M", "O", "G", "U", "S"]
def namegen(alphabet):
    for l in itertools.count():
        for name in itertools.product(alphabet, repeat=l):
            if name == tuple():
                continue
            yield ''.join(name)

namegeninst = namegen(alphabet)
known_states = {}

def obfuscate_state(state):
    if state not in known_states:
        known_states[state] = next(namegeninst)
    return known_states[state]



prog_begin = False
with open("turing.out") as f:
    with open("obfus.out", "w") as out:
        for line in f:
            if line.startswith("#"): # is a comment. Only add if program hadn't begun
                if not prog_begin:
                    out.write(line)
            elif line.startswith("start:") or line.startswith("accept:") or line.startswith("reject:"):
                prog_begin = True
                d = line.split(": ")
                print(d[0], obfuscate_state(d[1].strip()), sep=": ", file=out)
            elif line.startswith("blank:"):
                out.write(line)
            elif line.strip() != "":
                from_state, from_tape, arrow, to_state, to_tape, action = line.split()
                print(obfuscate_state(from_state), from_tape, arrow, obfuscate_state(to_state), to_tape, action, file=out)
                