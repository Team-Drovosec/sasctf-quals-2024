## Title
Vobla Tails

## Description
Got this one on my email today. Seems like fishing or whatever you professionals call it... Can you help?

## Solution
1. Attached PDF file contains a text from one of the "The Canterbury Tales" stories written by Geoffrey Chaucer. We can notice that the font used in this PDF appears to be custom and looks familiar, quite similar to the one used on competition platform. Let's check this file in various PDF viewers. Some of them will replace the custom emoji glyphs with the system or builtin ones, revealing us a hidden emoji at the line `At Lyeys was he⛳️and at Satalye,`. 

2. Let's extract this custom font from the PDF file in order to check what else may be hidden inside. It can be done with the use of `binwalk` tool:

```
binwalk -e vobla_tails.pdf
```

3. Output font has a TrueType format. We can analyze it using FontForge or Microsoft Visual TrueType (VTT). It does contain only glyphs used in the PDF. When we open the glyph U+26F3 (FLAG_IN_HOLE emoji), we see that there are other glyphs embedded in this glyph. We can see the flag by changing the zoom parameter. It's also possible to parse the TrueType file using the TTX tool, breaking down the embedded glyphs and plotting the graph with extracted points.

## Flag
SAS{tru3_typ3_i5_n0t_s0_tru3}

**Solved by:** 21 teams
