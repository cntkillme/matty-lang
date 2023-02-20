from mattylang.ast import *
from mattylang.symbols import SymbolTable


class Globals:
    def __init__(self):
        self.globals = SymbolTable()
        self.globals.register('print', extern=True, type=FunctionTypeNode(0, [AnyTypeNode(0)], NilTypeNode(0)))
