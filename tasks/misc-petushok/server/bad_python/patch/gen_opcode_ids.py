import sys
import re
import random

if __name__ == '__main__':
    with open(sys.argv[1],"r") as f:
        data = f.read()

    all_values = list()
    all_indexes = list()

    for m in re.finditer("^#define\s+(\S+)\s+(\d+)",data,flags = re.M):
        if m.group(1) not in ("HAVE_ARGUMENT","MIN_INSTRUMENTED_OPCODE"):
            all_indexes.append((m.start(2),m.end(2)))
            all_values.append(m.group(2))
            
    random.seed(42)
    random.shuffle(all_values)
            
    output = ''
    prev = 0
    for (i1,i2),value in zip(all_indexes,all_values):
        output += data[prev:i1] + value
        prev = i2    
    output += data[prev:]

    with open(sys.argv[1] + ".new","w") as f:
        f.write(output)

