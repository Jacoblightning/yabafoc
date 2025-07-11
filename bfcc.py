#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "bffuck",
# ]
# ///

import argparse
import os.path
import subprocess
from tabnanny import verbose
from unittest import case

from bffuck import BFFuck
from enum import Enum, auto

CODE = """
#include <stdio.h>

unsigned long long tape_ptr = 0;
unsigned char BUFFER[{tape_length}] = {{0}};

#define ptr_next() tape_ptr = (tape_ptr+1)%{tape_length}
#define ptr_prev() tape_ptr = (tape_ptr-1)%{tape_length}
#define inc()      BUFFER[tape_ptr]++
#define dec()      BUFFER[tape_ptr]--
#define out()      printf("%c", (char)BUFFER[tape_ptr])
#define in()       BUFFER[tape_ptr] = (unsigned char)getchar()

// Optimized IL Commands
#define set(x)     BUFFER[tape_ptr] = x
#define add(x)     BUFFER[tape_ptr] += x
#define sub(x)     BUFFER[tape_ptr] -= x
#define skip(x)    tape_ptr = (tape_ptr+x)%{tape_length}
#define back(x)    tape_ptr = (tape_ptr-x)%{tape_length}


int main(){{
    {program_code}
}}
"""

class IL(Enum):
    NEXT = auto()
    PREV = auto()
    INC  = auto()
    DEC  = auto()
    OUT  = auto()
    IN   = auto()
    LOOP = auto()
    ENDL = auto()

    # Unofficial IL used for optimizing
    SET  = auto()
    ADD = auto()
    SUB = auto()
    SKIP = auto()
    BACK = auto()


CONVERT_TABLE = {
    IL.NEXT: "ptr_next();",
    IL.PREV: "ptr_prev();",
    IL.INC:  "inc();",
    IL.DEC:  "dec();",
    IL.OUT:  "out();",
    IL.IN:   "in();",

    IL.LOOP: "while (BUFFER[tape_ptr]) {",
    IL.ENDL: "}",

    IL.SET: "set({operand});",
    IL.ADD: "add({operand});",
    IL.SUB: "sub({operand});",
    IL.SKIP: "skip({operand});",
    IL.BACK: "back({operand});",
}

def compile_il_to_c(bf, tape_length, emit_c):
    c_src = ""

    skipnext = False
    for c, il in enumerate(bf):
        if skipnext:
            skipnext = False
            continue

        match il:
            case IL.NEXT:
                c_src += CONVERT_TABLE[il]
            case IL.PREV:
                c_src += CONVERT_TABLE[il]
            case IL.INC:
                c_src += CONVERT_TABLE[il]
            case IL.DEC:
                c_src += CONVERT_TABLE[il]
            case IL.OUT:
                c_src += CONVERT_TABLE[il]
            case IL.IN:
                c_src += CONVERT_TABLE[il]
            case IL.LOOP:
                c_src += CONVERT_TABLE[il]
            case IL.ENDL:
                c_src += CONVERT_TABLE[il]

            case IL.SET:
                c_src += CONVERT_TABLE[il].format(operand=bf[c+1])
                skipnext = True
            case IL.ADD:
                c_src += CONVERT_TABLE[il].format(operand=bf[c+1])
                skipnext = True
            case IL.SUB:
                c_src += CONVERT_TABLE[il].format(operand=bf[c+1])
                skipnext = True
            case IL.SKIP:
                c_src += CONVERT_TABLE[il].format(operand=bf[c+1])
                skipnext = True
            case IL.BACK:
                c_src += CONVERT_TABLE[il].format(operand=bf[c+1])
                skipnext = True
            case _:
                raise ValueError("Unhandled il type")

        if emit_c:
            c_src += "\n"

    real_c_src = CODE.format(tape_length=tape_length, program_code=c_src)

    return real_c_src

def compile_c(c, output, verbose):
    subprocess.run(["gcc", "-x", "c", "-", "-o", output if output else "a.out"], input=c.encode(), stdout=None if verbose else subprocess.DEVNULL, check=True)

# "cleans" bf code; Removing comments and whitespace
def clean_bf(bf: str) -> list[str]:
    clean = []
    for line in bf.split("\n"):
        for char in line:
            # We follow both bf standards:
            # Any char that is not valid is ignored
            # and Anything after a # is ignored
            if char == "#":
                break

            if char not in [">", "<", "+", "-", ".", ",", "[", "]"]:
                continue

            clean.append(char)
    return clean

def optimize_il(il: list[IL]) -> list[IL|int]:
    new_il = []

    addcount = 0
    deccount = 0

    rcount = 0
    lcount = 0
    for c in range(len(il)):
        # Repeated increments
        if il[c] is IL.INC:
            addcount += 1
        else:
            if addcount > 1:
                new_il.append(IL.ADD)
                new_il.append(addcount)
                addcount = 0
            elif addcount == 1:
                new_il.append(IL.INC)
                addcount = 0

        # Repeated decrements
        if il[c] is IL.DEC:
            deccount += 1
        else:
            if deccount > 1:
                new_il.append(IL.SUB)
                new_il.append(deccount)
                deccount = 0
            elif deccount == 1:
                new_il.append(IL.DEC)
                deccount = 0

        # Repeated rights
        if il[c] is IL.NEXT:
            rcount += 1
        else:
            if rcount > 1:
                new_il.append(IL.SKIP)
                new_il.append(rcount)
                rcount = 0
            elif rcount == 1:
                new_il.append(IL.NEXT)
                rcount = 0

        # Repeated lefts
        if il[c] is IL.PREV:
            lcount += 1
        else:
            if lcount > 1:
                new_il.append(IL.BACK)
                new_il.append(lcount)
                lcount = 0
            elif lcount == 1:
                new_il.append(IL.PREV)
                lcount = 0

        # Optimizations past this point require a history of > 2
        if c < 2:
            if addcount == deccount == rcount == lcount == 0:
                new_il.append(il[c])
            continue

        # Set 0
        if il[c-2] is IL.LOOP and il[c-1] is IL.DEC and il[c] is IL.ENDL:
            del new_il[-2:]
            new_il.append(IL.SET)
            new_il.append(0)
            continue

        if addcount == deccount == rcount == lcount == 0:
            new_il.append(il[c])



    return new_il

def compile_bf_to_il(bf: list[str]):
    il = []
    for char in bf:
        match char:
            case ">":
                il.append(IL.NEXT)
            case "<":
                il.append(IL.PREV)
            case "+":
                il.append(IL.INC)
            case "-":
                il.append(IL.DEC)
            case ".":
                il.append(IL.OUT)
            case ",":
                il.append(IL.IN)
            case "[":
                il.append(IL.LOOP)
            case "]":
                il.append(IL.ENDL)
            case _:
                raise ValueError(f"Invalid Brainfuck: {char}")
    return il

def run_compiler(bf, tape_length, output, emit_c, verbose):
    if verbose:
        print("Step 1: Removing comments and whitespace...")
    bf_cleaned = clean_bf(bf)
    if verbose:
        print(f"Cleaned: {''.join(bf_cleaned)}")

        print("Step 2: Compiling to IL...")
    il: list[IL] = compile_bf_to_il(bf_cleaned)
    if verbose:
        print(f"IL: {', '.join([i.name for i in il])}")

        print("Step 3: Optimizing IL...")
    il = optimize_il(il)
    if verbose:
        str_il = []
        for i in il:
            if isinstance(i, IL):
                str_il.append(i.name)
            else:
                str_il.append(str(i))
        print(f"IL: {', '.join(str_il)}")

        print("Step 3: Compiling to C...")
    c_src = compile_il_to_c(il, tape_length, emit_c)

    if emit_c:
        print(c_src)
        return

    if verbose:
        print("Step 4: Compiling C Code...")
    compile_c(c_src, output, verbose)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The brainfuck file to compile")
    parser.add_argument("-o", "--output", help="The output compiled file")
    parser.add_argument("-t", "--tape-length", help="The length of the number tape", type=int, default=256)
    parser.add_argument("-f", "--flavour", help="The Brainfuck flavour to use", choices=["classic", "bffuck"], default="classic")
    parser.add_argument("--emit-c", help="Emit the intermediate C code and exit", action="store_true")
    parser.add_argument("-v", "--verbose", help="Make output more verbose", action="store_true")
    args = parser.parse_args()

    if args.tape_length < 1:
        print("Invalid tape length")
        exit(1)

    if not os.path.exists(args.input):
        print(f"{args.input} does not exist")
        exit(1)

    with open(args.input, "r") as srcfile:
        src = srcfile.read()

    if args.flavour == "bffuck":
        src = BFFuck().compile(src)


    run_compiler(src, args.tape_length, args.output, args.emit_c, args.verbose)

if __name__ == "__main__":
    main()
