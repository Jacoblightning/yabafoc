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
from enum import Enum


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

class IL(Enum):
	NEXT = 0
	PREV = 1
	INC  = 2
	DEC  = 3
	OUT  = 4
	IN   = 5
	LOOP = 6
	ENDL = 7


CONVERT_TABLE = {
	IL.NEXT: "ptr_next();",
	IL.PREV: "ptr_prev();",
	IL.INC:  "inc();",
	IL.DEC:  "dec();",
	IL.OUT:  "out();",
	IL.IN:   "in();",

	IL.LOOP: "while (BUFFER[tape_ptr]) {",
	IL.ENDL: "}"
}

def compile_il_to_c(bf, tape_length, emit_c):
	c_src = ""

	for il in bf:
		c_src += CONVERT_TABLE[il]
		if emit_c:
			c_src += "\n"

	real_c_src = CODE.format(tape_length=tape_length, program_code=c_src)

	return real_c_src

def compile_c(c, output, verbose):
	subprocess.run(["gcc", "-x", "c", "-", "-o", output if output else "a.out"], input=c.encode(), stdout=None if verbose else subprocess.DEVNULL, check=True)

# "cleans" bf code; Removing comments and whitespace
def clean_bf(bf):
	clean = ""
	for line in bf.split("\n"):
		for char in line:
			# We follow both bf standards:
			# Any char that is not valid is ignored
			# and Anything after a # is ignored
			if char == "#":
				break

			if char not in [">", "<", "+", "-", ".", ",", "[", "]"]:
				continue

			clean += char
	return clean

def compile_bf_to_il(bf):
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
		print(f"Cleaned: {bf_cleaned}")

	if verbose:
		print("Step 2: Compiling to IL...")
	il = compile_bf_to_il(bf_cleaned)

	if verbose:
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
