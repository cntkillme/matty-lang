from abc import ABC
from typing import TYPE_CHECKING, List, Optional

from mattylang.ast.core import AbstractNode, Declaration

if TYPE_CHECKING:
    from mattylang.ast.expression import ExpressionNode, IdentifierNode
    from mattylang.ast.type import TypeNode
    from mattylang.symbols import SymbolTable
    from mattylang.visitor import AbstractVisitor


class StatementNode(AbstractNode, ABC):
    pass


class ChunkNode(StatementNode):
    def __init__(self):
        super().__init__()
        self.statements: List[StatementNode] = []
        self.symbol_table: Optional[SymbolTable] = None

    def __str__(self):
        return f'chunk({len(self.statements)})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_chunk(self)

    def get_symbol_table(self) -> 'SymbolTable':
        assert self.symbol_table is not None, 'fatal: symbol table not set'
        return self.symbol_table


class VariableDefinitionNode(StatementNode, Declaration):
    def __init__(self, identifier: 'IdentifierNode', initializer: 'ExpressionNode'):
        super().__init__()
        identifier.parent = self
        initializer.parent = self
        self.identifier = identifier
        self.initializer = initializer
        self.invalid = identifier.invalid or initializer.invalid

    def __str__(self):
        return f'variable_definition({self.identifier})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_definition(self)

    def get_declared_name(self) -> str:
        return self.identifier.value

    def get_declared_type(self) -> 'TypeNode':
        return self.identifier.get_symbol().get_type()


class VariableAssignmentNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', value: 'ExpressionNode'):
        super().__init__()
        identifier.parent = self
        self.identifier = identifier
        value.parent = self
        self.value = value
        self.invalid = identifier.invalid or value.invalid

    def __str__(self):
        return f'variable_assignment({self.identifier})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_assignment(self)
