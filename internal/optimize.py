from .common import IL

import re
from functools import partial
from typing import Callable

def optimize_repeats(single: IL, multi: IL, il: list[IL|int]) -> list[IL|int]:
    new_il: list[IL|int] = []

    count = 0

    for c in il:
        if c is single:
            count += 1
            continue
        else:
            if count > 0:
                new_il.append(multi)
                new_il.append(count)
            count = 0
        new_il.append(c)
    return new_il

# Optimize [-] to one instruction
def optimize_zeros(il: list[IL|int]) -> list[IL|int]:
    new_il: list[IL|int] = []

    for c in range(len(il)):
        # The zeros optimization requires at least 2 previous ILs
        if c < 2:
            new_il.append(il[c])
            continue

        # Set 0
        if il[c-2] is IL.LOOP and il[c-1] is IL.DEC and il[c] is IL.ENDL:
            del new_il[-2:]
            new_il.append(IL.SET)
            new_il.append(0)
            continue

        new_il.append(il[c])
        
    return new_il

def unravel_loops(il: list[IL|int]) -> list[IL|int]:
    def optimize_loop_il(il: list[IL|int]):
        # Make sure the loop only contains arithmetic
        # Iterate through loop
        for i in il:
            if il not in [IL]:
                pass



    new_il: list[IL|int] = []

    
    # Code to find inner loops (loops with no more loops inside them)
    loop_ptr: int|None = None
    
    for c, il_code in enumerate(il):
        if il_code is IL.LOOP:
            loop_ptr = c
        if il_code is IL.ENDL:
            if loop_ptr is None:
                raise ValueError("] detected while not in a loop")
            print(f"Loop Ptr: {loop_ptr}\nLoop end Ptr: {c}")
            optimize_loop_il(il[loop_ptr+1:c])
                

    return il


# Optimization levels are simple: Call all level 1 opts, then all level 2 opts, etc...
OPTIMIZATIONS: list[list[Callable]] = [
    # Level 1 Optimizations
    [
        # Repeat Optimization
        *[partial(optimize_repeats, single=s, multi=m) for s, m in ((IL.INC, IL.ADD), (IL.DEC, IL.SUB), (IL.NEXT, IL.SKIP), (IL.PREV, IL.BACK))],
        # Optimize zeroing instructions
        optimize_zeros
    ],
    # Level 2 Optimizations
    [
        unravel_loops
    ]
]

def optimize_il(il: list[IL]) -> list[IL|int]:

    new_il = il

    for optimizations in OPTIMIZATIONS:
        for optimization in optimizations:
            new_il = optimization(il=new_il)
    
    return new_il
