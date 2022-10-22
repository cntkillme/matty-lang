from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import ScopedVisitor


class Interpreter(ScopedVisitor):
    def __init__(self, module: Module):
        super().__init__(module)
