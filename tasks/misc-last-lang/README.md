## Title
Last Lang

## Description
We found some kind of programme from the future, it seems that human language has evolved into 🕳 😅

## Solution
- To get the flag, we need to execute the corresponding instruction
- We can't execute it right away because we are not admin and existence of a flag instruction is checked
- We can't execute it straight ahead, because we are not admin and it is checked
- The decision about whether there is a flag instruction is cached in the set by hash
- Hash for instructions with an array inside is calculated in a non-serializable way (first data, then length)
- Submit two programs that generate the same hash: the first one will mark it as safe, the second one will print the flag
    - Example:
        - put[R0] 00 00 00 00 00 00 00 00 08 00 07 00 mov[R0] 0 mov[R0] 0 print[R0] 26
        - put[R0] flag[R0] print[R0] 12 inc[R0] inc[R0] inc[R0] inc[R1] inc[R0] mov[R0] 0 print[R0] 26

## Flag
Dynamic container flag

**Solved by:** 1 team