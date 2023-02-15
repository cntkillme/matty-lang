from mattylang.ast import *
from mattylang.symbols import SymbolTable


class Globals:
    def __init__(self):
        self.globals = SymbolTable()
        self.globals.register('print', extern=True, type=FunctionTypeNode([AnyTypeNode()], NilTypeNode()))
