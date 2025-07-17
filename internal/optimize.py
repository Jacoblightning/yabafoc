import re
from functools import partial
from typing import Callable

from .common import (
    BF_IL,
    IL_Add,
    IL_Back,
    IL_Copy,
    IL_Endl,
    IL_In,
    IL_Loop,
    IL_Mul,
    IL_Out,
    IL_Set,
    IL_Skip,
    IL_Sub,
    Optimized_Arithemetic_IL,
    Optimized_IL,
)

# Coded with references, help, and some shameless stealing from https://github.com/matslina/bfoptimization


def optimize_repeats(
    single: BF_IL, multi: Optimized_IL, il: list[BF_IL | Optimized_IL]
) -> list[BF_IL | Optimized_IL]:
    new_il: list[BF_IL | Optimized_IL] = []

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
        if (
            isinstance(il[c - 2], IL_Loop)
            and isinstance(il[c - 1], IL_Sub)
            and il[c - 1].operand == 1
            and isinstance(il[c], IL_Endl)
        ):
            del new_il[-2:]
            new_il.append(IL_Set(0))
            continue

        new_il.append(il[c])

    return new_il


def unravel_loops(il: list[Optimized_IL]) -> list[Optimized_IL]:
    def optimize_loop_il(il: list[Optimized_IL]) -> list[Optimized_IL] | None:
        # Make sure the loop only contains arithmetic
        # Iterate through loop. Could probably be replaced by a comprehension and any()
        for i in il:
            if not issubclass(i.__class__, Optimized_Arithemetic_IL):
                # This loop is not just arithmetic. We can't optimize it
                return None

        # List is good

        mem, p = {}, 0

        for i in il:
            match i:
                case IL_Skip(operand=x):
                    p += x
                case IL_Back(operand=x):
                    p -= x
                case IL_Add(operand=x):
                    mem[p] = mem.get(p, 0) + x
                case IL_Sub(operand=x):
                    mem[p] = mem.get(p, 0) - x
                case _:
                    raise ValueError(f"???? Unknown IL: {i}")

        if p != 0 or mem.get(0, 0) != -1:
            # We can't optimize this loop :(
            return None

        # We can optimize this!

        optimized = []

        for k, v in mem.items():
            if k == 0:
                # The original
                continue

            if v == 1:
                optimized.append(IL_Copy(k))
            else:
                optimized.append(IL_Mul(k, v))

        # Don't forget the side effect!!!!!
        optimized.append(IL_Set(0))
        return optimized

    new_il: list[Optimized_IL] = []

    # Code to find inner loops (loops with no more loops inside them)
    loop_ptr: int | None = None

    for c, il_code in enumerate(il):
        new_il.append(il_code)
        if isinstance(il_code, IL_Loop):
            loop_ptr = c
        if isinstance(il_code, IL_Endl) and loop_ptr is not None:
            opt = optimize_loop_il(il[loop_ptr + 1 : c])
            # Used for calculating the correct index for new_il
            loop_length = c - loop_ptr
            # The ref to the start of the loop is no longer valid
            loop_ptr = None
            if opt is not None:
                # Delete the old loop from the IL
                del new_il[len(new_il) - loop_length - 1 :]
                new_il.extend(opt)

    return new_il


def convert_bf_to_optimized_il(il: list[BF_IL]) -> list[Optimized_IL]:
    intermediate: list[BF_IL | Optimized_IL] = il

    for s, m in (
        (BF_IL.INC, IL_Add),
        (BF_IL.DEC, IL_Sub),
        (BF_IL.NEXT, IL_Skip),
        (BF_IL.PREV, IL_Back),
    ):
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


def optimize_undos(il: list[Optimized_IL]) -> list[Optimized_IL]:
    new_il: list[Optimized_IL] = []

    to_optimize = [{IL_Sub, IL_Add}, {IL_Skip, IL_Back}]

    for i in range(len(il)):
        if i < 1:
            new_il.append(il[i])
            continue

        if {il[i].__class__, il[i - 1].__class__} in to_optimize:
            del new_il[-1]

            # Dont need to do any calculations if they have equal operands
            if il[i].operand == il[i - 1].operand:
                continue

            if isinstance(il[i], IL_Add):
                assert isinstance(il[i - 1], IL_Sub)
                newadd = il[i].operand - il[i - 1].operand
                if newadd > 0:
                    new_il.append(IL_Add(newadd))
                else:
                    new_il.append(IL_Sub(-newadd))
            elif isinstance(il[i], IL_Skip):
                assert isinstance(il[i - 1], IL_Back)
                newskip = il[i].operand - il[i - 1].operand
                if newskip > 0:
                    new_il.append(IL_Skip(newskip))
                else:
                    new_il.append(IL_Back(-newskip))
            elif isinstance(il[i], IL_Sub):
                assert isinstance(il[i - 1], IL_Add)
                newsub = il[i].operand - il[i - 1].operand
                if newsub > 0:
                    new_il.append(IL_Sub(newsub))
                else:
                    new_il.append(IL_Add(-newsub))
            elif isinstance(il[i], IL_Back):
                assert isinstance(il[i - 1], IL_Skip)
                newback = il[i].operand - il[i - 1].operand
                if newback > 0:
                    new_il.append(IL_Back(newback))
                else:
                    new_il.append(IL_Skip(-newback))
            else:
                raise ValueError("Impossible Situation!")
        else:
            new_il.append(il[i])

    return new_il

def remove_unreachable_loops(il: list[Optimized_IL]) -> list[Optimized_IL]:
    new_il: list[Optimized_IL] = []

    wait = 0
    for c, il_code in enumerate(il):
        if wait != 0:
            # We are currently in the process of removing a loop. Ignore everything except for loop modifiers
            if isinstance(il_code, IL_Loop):
                wait += 1
            elif isinstance(il_code, IL_Endl):
                wait -= 1
            continue

        if c == 0 and isinstance(il_code, IL_Loop):
            # If the first instruction is a loop, skip it
            wait = 1
            continue

        # If the il is a loop, it cannot be the first il and so it is safe to check il[c-1]
        # If the previous instruction was a set(0) or another loop
        if isinstance(il_code, IL_Loop) and ((isinstance(il[c-1], IL_Set) and il[c-1].operand == 0) or isinstance(il[c-1], IL_Endl)):
            wait = 1
            continue

        new_il.append(il_code)


    return new_il
            
        


# Optimizations. CALL THESE IN ORDER!!
OPTIMIZATIONS: list[Callable] = [
    # Optimize zeroing instructions
    optimize_zeros,
    # Optimize undoing instructions such as +++-- to +
    optimize_undos,
    # Remove unreachable loops
    remove_unreachable_loops,
    # Unravel loops to turn [->++<] into a mul(1, 2) il
    unravel_loops,
]


def optimize_il(il: list[BF_IL]) -> list[Optimized_IL]:

    new_il = convert_bf_to_optimized_il(il)

    for optimization in OPTIMIZATIONS:
        new_il = optimization(il=new_il)

    return new_il
