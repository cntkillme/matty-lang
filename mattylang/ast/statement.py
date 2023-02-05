from abc import ABC
from typing import TYPE_CHECKING, List, Optional

from mattylang.ast.core import AbstractNode, Declaration

if TYPE_CHECKING:
    from mattylang.ast.expression import ExpressionNode, IdentifierNode, CallExpressionNode
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

    def get_declared_scope(self) -> 'SymbolTable':
        symbol = self.identifier.symbol
        assert symbol is not None, 'fatal: symbol not set'
        return symbol.scope


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
        super().__init__()

    def __str__(self):
        return f'break_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_break_statement(self)

    def get_enclosing_loop_statement(self):
        return self.get_first_ancestor(lambda parent: isinstance(parent, WhileStatementNode))


class ContinueStatementNode(StatementNode):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return f'continue_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_continue_statement(self)

    def get_enclosing_loop_statement(self):
        return self.get_first_ancestor(lambda parent: isinstance(parent, WhileStatementNode))


class FunctionDefinitionNode(StatementNode, Declaration):
    def __init__(self, identifier: 'IdentifierNode', parameters: List[VariableDefinitionNode], body: StatementNode):
        super().__init__()
        identifier.parent = self
        self.identifier = identifier
        for parameter in parameters:
            parameter.parent = self
        self.parameters = parameters
        body.parent = self
        self.body = body
        self.invalid = identifier.invalid or any(parameter.invalid for parameter in parameters) or body.invalid

    def __str__(self):
        return f'function_definition({self.identifier}): ({", ".join(parameter.value for parameter in self.parameters)})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_function_definition(self)

    def get_declared_name(self) -> str:
        return self.identifier.value

    def get_declared_type(self) -> 'TypeNode':
        symbol = self.identifier.symbol
        assert symbol is not None, 'fatal: symbol not set'
        assert symbol.type is not None, 'fatal: symbol type not set'
        return symbol.type

    def get_declared_scope(self) -> 'SymbolTable':
        symbol = self.identifier.symbol
        assert symbol is not None, 'fatal: symbol not set'
        return symbol.scope


class ReturnStatementNode(StatementNode):
    def __init__(self, value: Optional['ExpressionNode'] = None):
        super().__init__()
        if value:
            value.parent = self
            self.invalid = value.invalid
        self.value = value

    def __str__(self):
        return f'return_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_return_statement(self)

    def get_enclosing_function_definition(self):
        return self.get_first_ancestor(lambda parent: isinstance(parent, FunctionDefinitionNode))


class CallStatementNode(StatementNode):
    def __init__(self, call_expression: 'CallExpressionNode'):
        super().__init__()
        self.call_expression = call_expression

    def __str__(self):
        return f'call_statement({self.call_expression})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_call_statement(self)
