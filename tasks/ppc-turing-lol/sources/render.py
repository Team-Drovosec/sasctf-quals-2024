#!/usr/bin/env python3

from jinja2 import Template
from jinja2.filters import FILTERS


def bsl(value, n=0):
    return value >> n

def band(value, b=0):
    return value & b

def fhex(value) :
    return hex(value)[2:]


FILTERS["bsl"] = bsl
FILTERS["band"] = band
FILTERS["hex"] = fhex

with open("turing.txt") as f:
    with open("turing.out", "w") as f2:
        f2.write(Template(f.read(), trim_blocks=True, lstrip_blocks=True).render())