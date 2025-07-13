from enum import Enum, auto

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
