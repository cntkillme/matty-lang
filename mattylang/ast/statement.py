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
        symbol = self.identifier.symbol
        assert symbol is not None, 'fatal: symbol not set'
        assert symbol.type is not None, 'fatal: symbol type not set'
        return symbol.type


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


class IfStatementNode(StatementNode):
    def __init__(self, condition: 'ExpressionNode', if_body: StatementNode, else_body: Optional[StatementNode] = None):
        super().__init__()
        condition.parent = self
        self.condition = condition
        if_body.parent = self
        self.if_body = if_body
        if else_body is not None:
            else_body.parent = self
        self.else_body = else_body
        self.invalid = condition.invalid or if_body.invalid or (else_body is not None and else_body.invalid)

    def __str__(self):
        return f'if_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_if_statement(self)


class WhileStatementNode(StatementNode):
    def __init__(self, condition: 'ExpressionNode', body: StatementNode):
        super().__init__()
        condition.parent = self
        self.condition = condition
        body.parent = self
        self.body = body
        self.invalid = condition.invalid or body.invalid

    def __str__(self):
        return f'while_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_while_statement(self)


class BreakStatementNode(StatementNode):
    def __init__(self):
        self.enclosing_loop_statement: Optional['WhileStatementNode'] = None
        super().__init__()

    def __str__(self):
        return f'break_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_break_statement(self)


class ContinueStatementNode(StatementNode):
    def __init__(self):
        self.enclosing_loop_statement: Optional['WhileStatementNode'] = None
        super().__init__()

    def __str__(self):
        return f'continue_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_continue_statement(self)
