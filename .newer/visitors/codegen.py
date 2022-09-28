from compiler.nodes import *
from compiler.visitor import AbstractVisitor


class CodegenVisitor(AbstractVisitor):
    def __init__(self):
        pass

    def visit_program(self, program: ProgramNode) -> None:
        raise NotImplementedError('codegen not yet implemented')
