from .common import BF_IL, Optimized_IL, Optimized_Arithemetic_IL, IL_Out, IL_In, IL_Loop, IL_Endl, IL_Set, IL_Add, IL_Sub, IL_Skip, IL_Back

import re
from functools import partial
from typing import Callable

# Coded with references, help, and some shameless stealing from https://github.com/matslina/bfoptimization

def optimize_repeats(single: BF_IL, multi: Optimized_IL, il: list[BF_IL|Optimized_IL]) -> list[BF_IL|Optimized_IL]:
    new_il: list[BF_IL|Optimized_IL] = []

    count = 0

    for c in il:
        if c is single:
            count += 1
            continue
        if count > 0:
            new_il.append(multi(count))
            count = 0
        new_il.append(c)
    return new_il

# Optimize [-] to one instruction
def optimize_zeros(il: list[Optimized_IL]) -> list[Optimized_IL]:
    new_il: list[Optimized_IL] = []

    for c in range(len(il)):
        # The zeros optimization requires at least 2 previous ILs
        if c < 2:
            new_il.append(il[c])
            continue

        # Set 0
        if isinstance(il[c-2], IL_Loop) and isinstance(il[c-1], IL_Sub) and il[c-1].operand == 1 and isinstance(il[c], IL_Endl):
            del new_il[-2:]
            new_il.append(IL_Set(0))
            continue

        new_il.append(il[c])
        
    return new_il

def unravel_loops(il: list[Optimized_IL]) -> list[Optimized_IL]:
    def optimize_loop_il(il: list[Optimized_IL]) -> list[Optimized_IL]:
        # Make sure the loop only contains arithmetic
        # Iterate through loop. Could probably be replaced by a comprehension and any()
        for i in il:
            if not issubclass(i.__class__, Optimized_Arithemetic_IL):
                # This loop is not just arithmetic. We can't optimize it
                return il

        # List is good

        mem, p = {}, 0

        for i in il:
            pass
        
        return il



    new_il: list[Optimized_IL] = []

    
    # Code to find inner loops (loops with no more loops inside them)
    loop_ptr: int|None = None
    
    for c, il_code in enumerate(il):
        if isinstance(il_code, IL_Loop):
            loop_ptr = c
        if isinstance(il_code, IL_Endl):
            if loop_ptr is None:
                raise ValueError("] detected while not in a loop")
            print(f"Loop Ptr: {loop_ptr}\nLoop end Ptr: {c}")
            optimize_loop_il(il[loop_ptr+1:c])
                

    return il

def convert_bf_to_optimized_il(il: list[BF_IL]) -> list[Optimized_IL]:
    intermediate: list[BF_IL|Optimized_IL] = il

    for s, m in ((BF_IL.INC, IL_Add), (BF_IL.DEC, IL_Sub), (BF_IL.NEXT, IL_Skip), (BF_IL.PREV, IL_Back)):
        intermediate = optimize_repeats(s, m, intermediate)

    new_il: list[Optimized_IL] = []

    for i in intermediate:
        if i is BF_IL.LOOP:
            new_il.append(IL_Loop())
            continue
        if i is BF_IL.ENDL:
            new_il.append(IL_Endl())
            continue
        if i is BF_IL.OUT:
            new_il.append(IL_Out())
            continue
        if i is BF_IL.IN:
            new_il.append(IL_In())
            continue
        new_il.append(i)

    return new_il



# Optimization levels are simple: Call all level 1 opts, then all level 2 opts, etc...
OPTIMIZATIONS: list[list[Callable]] = [
    # Level 1 Optimizations
    [
        # Optimize zeroing instructions
        optimize_zeros
    ],
    # Level 2 Optimizations
    [
        unravel_loops
    ]
]

def optimize_il(il: list[BF_IL]) -> list[Optimized_IL]:

    new_il = convert_bf_to_optimized_il(il)

    for optimizations in OPTIMIZATIONS:
        for optimization in optimizations:
            new_il = optimization(il=new_il)
    
    return new_il
