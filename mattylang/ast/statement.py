from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from mattylang.ast.core import AbstractNode, NodeList

if TYPE_CHECKING:
    from mattylang.ast.expression import ExpressionNode, IdentifierNode
    from mattylang.symbols import Scope
    from mattylang.visitor import AbstractVisitor


class StatementNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)


class ChunkNode(StatementNode):
    def __init__(self):
        super().__init__('chunk')
        self.statements = NodeList[StatementNode](self)
        self.scope: Optional['Scope'] = None

    def __str__(self):
        return f'chunk({len(self.statements)})'

    def add_statement(self, statement: StatementNode):
        self.statements.add_node(statement)
        self.invalid = self.invalid or statement.invalid

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_chunk(self)


class VariableDefinitionNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', initializer: 'ExpressionNode'):
        super().__init__('variable_definition')
        identifier.parent = self
        initializer.parent = self
        self.identifier = identifier
        self.__initializer = initializer
        self.invalid = identifier.invalid or initializer.invalid
        self.constant = False

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_definition(self)

    @property
    def initializer(self):
        return self.__initializer

    @initializer.setter
    def initializer(self, initializer: 'ExpressionNode'):
        initializer.parent = self
        self.__initializer = initializer


class VariableAssignmentNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', initializer: 'ExpressionNode'):
        super().__init__('variable_assignment')
        self.identifier = identifier
        self.__operand = initializer
        self.invalid = identifier.invalid or initializer.invalid
        identifier.parent = self
        initializer.parent = self

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_assignment(self)

    @property
    def value(self):
        return self.__operand

    @value.setter
    def value(self, initializer: 'ExpressionNode'):
        initializer.parent = self
        self.__operand = initializer
