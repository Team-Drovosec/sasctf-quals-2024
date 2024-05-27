## Title
ebin

## Description
Hello, dear bruh. \
Do you know that once upon a time there were cute small Ebins walking around the planet? \
And with the each day passed they evolved, mastered something new... \
And of course... \
They were breeding... \
They were becoming more and more perfect... \
The Ebins developed their own languages... \
And even philosophy... \
The Ebins wrote and listened to music... \
And of course they danced to it... \
And they applauded to each other... \
The Ebins went so far in their brogress that they invented anime... \
But after... \
The snakes came up to something terrible...

## Solution
The application seems to be some kind of crackme packed with pyinstaller.
1. Decompile the python code with pycdc. It may miss some lines depending on the version but you still can recover them from bytecode.
2. Significant part of the code is hidden in two types of shellcodes - `pyc` and `asm`
- Python shellcodes are constructed with `function` and `code` types
- Assembler shellcodes are spawned with `ctypes` and casted to a callable function with `ctypes.WINFUNCTYPE`. There's also a master-shellcode that does the decryption of other shellcodes.
3. Python shellcodes can be reversed with the help of `dis`. Assembler shellcodes can be either debugged in runtime or analyzed statically with disassemblers.
4. After figuring out what each shellcode does we can see that all changes are reversible.
5. Inverse wrong but working implementation of RC5 (this implementation can sometimes be found in real world malware due to the fact it's a second url when you google "github rc5 c" - https://gist.github.com/gcolvin/7a0f251f71b7f46251d3400add8fd703)
6. Inverse three partial encodings of the secret
8. You got the flag!

Solver in /writeup

## Flag
SAS{h3_1S_do1n6_l3g_3x3rC1s3}

**Solved by:** 11 teams