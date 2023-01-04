from typing import TYPE_CHECKING

from mattylang.ast.core import AbstractNode

if TYPE_CHECKING:
    from mattylang.ast.statement import ChunkNode
    from mattylang.visitor import AbstractVisitor


class ProgramNode(AbstractNode):
    def __init__(self, chunk: 'ChunkNode'):
        super().__init__()
        self.chunk = chunk
        self.invalid = chunk.invalid

    def __str__(self):
        return f'program'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_program(self)
