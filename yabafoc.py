#!/usr/bin/env -S uv run --script
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

from internal.common import BF_IL
from internal.optimize import optimize_il

CODE = """
#include <stdio.h>

unsigned long long tape_ptr = 0;
unsigned char BUFFER[{tape_length}] = {{0}};

#define offset_safe(x)  ((tape_ptr+(x))%{tape_length})
#define offset_unsafe(x)  (tape_ptr+(x))

#define offset {offset}

#define out()      putchar((char)BUFFER[tape_ptr])
#define in()       BUFFER[tape_ptr] = (unsigned char)getchar()
#define set(x)     BUFFER[tape_ptr] = x
#define add(x)     BUFFER[tape_ptr] += x
#define sub(x)     BUFFER[tape_ptr] -= x
#define skip(x)    tape_ptr = offset(x)
#define back(x)    tape_ptr = offset(-(x))

#define copy(x)    BUFFER[offset(x)] += BUFFER[tape_ptr]
#define mul(x, m)  BUFFER[offset(x)] += (BUFFER[tape_ptr] * m)


int main(){{
    {program_code}
}}
"""


def compile_il_to_c(bf, tape_length, emit_c, unsafe_opts):
    c_src = ""

    for c, il in enumerate(bf):
        c_src += il.convert()

        if emit_c:
            c_src += "\n"

    real_c_src = CODE.format(
        tape_length=tape_length,
        program_code=c_src,
        offset="offset_unsafe" if unsafe_opts else "offset_safe",
    )

    return real_c_src


def compile_c(c, output, verbose):
    subprocess.run(
        [
            "gcc",
            "-x",
            "c",
            "-O3",
            "-s",
            "-funsigned-char",
            "-",
            "-o",
            output if output else "a.out",
        ],
        input=c.encode(),
        stdout=None if verbose else subprocess.DEVNULL,
        check=True,
    )


# "cleans" bf code; Removing comments and whitespace
def clean_bf(bf: str, dlc: bool) -> list[str]:
    clean = []
    for line in bf.split("\n"):
        for char in line:
            # We follow both bf standards:
            # Any char that is not valid is ignored
            # and anything after a # is ignored
            if char == "#" and not dlc:
                break

            if char not in [">", "<", "+", "-", ".", ",", "[", "]"]:
                continue

            clean.append(char)
    return clean


def compile_bf_to_il(bf: list[str]):
    il = []
    for char in bf:
        match char:
            case ">":
                il.append(BF_IL.NEXT)
            case "<":
                il.append(BF_IL.PREV)
            case "+":
                il.append(BF_IL.INC)
            case "-":
                il.append(BF_IL.DEC)
            case ".":
                il.append(BF_IL.OUT)
            case ",":
                il.append(BF_IL.IN)
            case "[":
                il.append(BF_IL.LOOP)
            case "]":
                il.append(BF_IL.ENDL)
            case _:
                raise ValueError(f"Invalid Brainfuck: {char}")
    return il


def run_compiler(bf, tape_length, output, emit_c, verbose, unsafe_opts, dlc):
    if verbose:
        print("Step 1: Removing comments and whitespace...")
    bf_cleaned = clean_bf(bf, dlc)
    if verbose:
        print(f"Cleaned: {''.join(bf_cleaned)}")

        print("Step 2: Compiling to IL...")
    il: list[IL] = compile_bf_to_il(bf_cleaned)
    if verbose:
        print(f"IL: {', '.join([i.name for i in il])}")

        print("Step 3: Optimizing IL...")
    il = optimize_il(il, tape_length)
    if verbose:
        print(f"IL: {', '.join(map(repr, il))}")

        print("Step 3: Compiling to C...")
    c_src = compile_il_to_c(il, tape_length, emit_c, unsafe_opts)

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
    parser.add_argument(
        "-t",
        "--tape-length",
        help="The length of the number tape",
        type=int,
        default=512,
    )
    parser.add_argument(
        "-f",
        "--flavour",
        help="The Brainfuck flavour to use",
        choices=["classic", "bffuck"],
        default="classic",
    )
    parser.add_argument(
        "--unsafe-optimizations",
        help="Enable unsafe optimizations that can crash the program if the pointer goes off the tape. You SHOULD enable this if you can, in some cases it can make the program much faster. It is disabled by default to prevent broken programs from crashing.",
        action="store_true",
    )
    parser.add_argument(
        "--disable-line-comment",
        help="Disallow using # for line comment and treat it as a char comment instead. This fixes some programs which (stupidly) use # in the middle of a code line",
        action="store_true",
    )
    parser.add_argument(
        "--emit-c", help="Emit the intermediate C code and exit", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="Make output more verbose", action="store_true"
    )
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

    run_compiler(
        src,
        args.tape_length,
        args.output,
        args.emit_c,
        args.verbose,
        args.unsafe_optimizations,
        args.disable_line_comment,
    )


if __name__ == "__main__":
    main()
