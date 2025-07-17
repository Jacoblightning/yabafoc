from enum import Enum, auto


class BF_IL(Enum):
    NEXT = auto()
    PREV = auto()
    INC = auto()
    DEC = auto()
    OUT = auto()
    IN = auto()
    LOOP = auto()
    ENDL = auto()


class Optimized_IL:
    def __repr__(self):
        if hasattr(self, "op2"):
            return f"{self.__class__.__name__}({self.op}, {self.op2})"
        if hasattr(self, "operand"):
            return f"{self.__class__.__name__}({self.operand})"
        return self.__class__.__name__


class Optimized_Arithemetic_IL(Optimized_IL):
    pass


class IL_Out(Optimized_IL):
    def convert(self):
        return "out();"


class IL_In(Optimized_IL):
    def convert(self):
        return "in();"


class IL_Loop(Optimized_IL):
    def convert(self):
        return "while (BUFFER[tape_ptr]) {"


class IL_Endl(Optimized_IL):
    def convert(self):
        return "}"


class IL_Set(Optimized_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"set({self.operand});"


class IL_Add(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"add({self.operand});"


class IL_Sub(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"sub({self.operand});"


class IL_Skip(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"skip({self.operand});"


class IL_Back(Optimized_Arithemetic_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"back({self.operand});"


class IL_Copy(Optimized_IL):
    def __init__(self, x):
        self.operand = x

    def convert(self):
        return f"copy({self.operand});"


class IL_Mul(Optimized_IL):
    def __init__(self, x, m):
        self.op = x
        self.op2 = m

    def convert(self):
        return f"mul({self.op}, {self.op2});"
