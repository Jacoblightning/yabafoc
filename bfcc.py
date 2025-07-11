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
from bffuck import BFFuck


CODE = """
#include <stdio.h>

unsigned long long tape_ptr = 0;
unsigned char BUFFER[{tape_length}] = {{0}};

#define ptr_next() tape_ptr = (tape_ptr+1)%{tape_length}
#define ptr_prev() tape_ptr = (tape_ptr-1)%{tape_length}
#define inc()      BUFFER[tape_ptr]++
#define dec()      BUFFER[tape_ptr]--
#define out()      printf("%c", (char)BUFFER[tape_ptr])
#define in()       BUFFER[tape_ptr] = (unsigned char)getchar();


int main(){{
    {program_code}
}}
"""

CONVERT_TABLE = {
    ">": "ptr_next();",
    "<": "ptr_prev();",
    "+": "inc();",
    "-": "dec();",
    ".": "out();",
    ",": "in();",
    
    "[": "while (BUFFER[tape_ptr]) {",
    "]": "}"
}

def compile_bf_to_c(bf, tape_length, verbose):
    c_src = ""

    for char in bf:
        c_src += CONVERT_TABLE[char]
        if verbose:
	        c_src += "\n"

    real_c_src = CODE.format(tape_length=tape_length, program_code=c_src)

    return real_c_src

def compile_c(c, output, verbose):
	subprocess.run(["gcc", "-x", "c", "-", "-o", output if output else "a.out"], input=c.encode(), stdout=None if verbose else subprocess.DEVNULL, check=True)

# "cleans" bf code; Removing comments and whitespace
def clean_bf(bf):
    clean = ""
    lines = bf.split("\n")
    for line in bf:
        for char in line:
		    # We follow both bf standards:
		    # Any char that is not valid is ignored
		    # and Anything after a # is ignored
	        if char == "#":
		        break

	        if char not in CONVERT_TABLE:
		        continue
		    
	        clean += char
    return clean



def run_compiler(bf, tape_length, output, emit_c, verbose):
    bf_cleaned = clean_bf(bf)

    c_src = compile_bf_to_c(bf_cleaned, tape_length, verbose)

    if emit_c:
        print(c_src)
        return
        
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
