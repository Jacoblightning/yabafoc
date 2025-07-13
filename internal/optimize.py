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
