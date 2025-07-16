from enum import Enum, auto

class BF_IL(Enum):
    NEXT = auto()
    PREV = auto()
    INC  = auto()
    DEC  = auto()
    OUT  = auto()
    IN   = auto()
    LOOP = auto()
    ENDL = auto()

class Optimized_IL:
    def __repr__(self):
        if hasattr(self, "operand"):
            return f"{self.__class__.__name__}({self.operand})"
        return self.__class__.__name__

class Optimized_Arithemetic_IL(Optimized_IL):
    pass

class IL_Out(Optimized_IL):
    pass

class IL_In(Optimized_IL):
    pass

class IL_Loop(Optimized_IL):
    pass

class IL_Endl(Optimized_IL):
    pass

class IL_Set(Optimized_IL):
    def __init__(self, x):
        self.operand = x

class IL_Add(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

class IL_Sub(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

class IL_Skip(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

class IL_Back(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

CONVERT_TABLE = {
    IL_Loop: "while (BUFFER[tape_ptr]) {",
    IL_Endl: "}",

    IL_Set:  "set({operand});",
    IL_Add:  "add({operand});",
    IL_Sub:  "sub({operand});",
    IL_Skip: "skip({operand});",
    IL_Back: "back({operand});",

    IL_Out:  "out();",
    IL_In:   "in();",
}
