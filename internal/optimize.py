from .common import IL

def optimize_repeats(il: list[IL|int], single: IL, multi: IL) -> list[IL|int]:
    new_il: list[IL|int] = []

    count = 0

    for c in il:
        if c is single:
            count += 1
            continue
        else:
            if count > 1:
                new_il.append(multi)
                new_il.append(count)
            elif count == 1:
                new_il.append(single)
            count = 0
        new_il.append(c)
    return new_il
            
def optimize_zeros(il: list[IL|int]) -> list[IL|int]:
    new_il = []

    for c in range(len(il)):
        # Optimizations past this point require a history of > 2
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

def optimize_il(il: list[IL]) -> list[IL|int]:

    new_il = il

    for s, m in ((IL.INC, IL.ADD), (IL.DEC, IL.SUB), (IL.NEXT, IL.SKIP), (IL.PREV, IL.BACK)):
        new_il = optimize_repeats(new_il, s, m)

    new_il = optimize_zeros(new_il)
    
    return new_il
