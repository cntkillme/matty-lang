from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mattylang.module import Module

if TYPE_CHECKING:
    from mattylang.nodes import *


class AbstractVisitor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def visit_program(self, node: 'ProgramNode'):
        self.visit_chunk(node.chunk)
        node.invalid = node.invalid or node.chunk.invalid

    def visit_chunk(self, node: 'ChunkNode'):
        for statement in node.statements:
            statement.accept(self)
            node.invalid = node.invalid or statement.invalid

    def visit_variable_definition(self, node: 'VariableDefinitionNode'):
        node.initializer.accept(self)
        node.identifier.accept(self)
        node.invalid = node.invalid or node.identifier.invalid or node.initializer.invalid

    def visit_variable_assignment(self, node: 'VariableAssignmentNode'):
        node.identifier.accept(self)
        node.value.accept(self)
        node.invalid = node.invalid or node.identifier.invalid or node.value.invalid

    def visit_if_statement(self, node: 'IfStatementNode'):
        node.condition.accept(self)
        node.if_body.accept(self)
        if node.else_body is not None:
            node.else_body.accept(self)
        node.invalid = node.invalid or node.condition.invalid or node.if_body.invalid or (
            node.else_body is not None and node.else_body.invalid)

    def visit_while_statement(self, node: 'WhileStatementNode'):
        node.condition.accept(self)
        node.body.accept(self)
        node.invalid = node.invalid or node.condition.invalid or node.body.invalid

    def visit_break_statement(self, node: 'BreakStatementNode'):
        pass

    def visit_continue_statement(self, node: 'ContinueStatementNode'):
        pass

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        node.identifier.accept(self)
        node.invalid = node.invalid or node.identifier.invalid
        for parameter in node.parameters:
            parameter.accept(self)
            node.invalid = node.invalid or parameter.invalid
        node.body.accept(self)
        node.invalid = node.invalid or node.body.invalid

    def visit_return_statement(self, node: 'ReturnStatementNode'):
        if node.value is not None:
            node.value.accept(self)
            node.invalid = node.invalid or node.value.invalid

    def visit_call_statement(self, node: 'CallStatementNode'):
        node.call_expression.accept(self)

    def visit_unary_expression(self, node: 'UnaryExpressionNode'):
        node.operand.accept(self)
        node.invalid = node.invalid or node.operand.invalid

    def visit_binary_expression(self, node: 'BinaryExpressionNode'):
        node.left.accept(self)
        node.right.accept(self)
        node.invalid = node.invalid or node.left.invalid or node.right.invalid

    def visit_nil_literal(self, node: 'NilLiteralNode'):
        pass

    def visit_bool_literal(self, node: 'BoolLiteralNode'):
        pass

    def visit_real_literal(self, node: 'RealLiteralNode'):
        pass

    def visit_string_literal(self, node: 'StringLiteralNode'):
        pass

    def visit_identifier(self, node: 'IdentifierNode'):
        pass

    def visit_call_expression(self, node: 'CallExpressionNode'):
        node.identifier.accept(self)
        node.invalid = node.invalid or node.identifier.invalid
        for argument in node.arguments:
            argument.accept(self)
            node.invalid = node.invalid or argument.invalid

    def visit_nil_type(self, node: 'NilTypeNode'):
        pass

    def visit_bool_type(self, node: 'BoolTypeNode'):
        pass

    def visit_real_type(self, node: 'RealTypeNode'):
        pass

    def visit_string_type(self, node: 'StringTypeNode'):
        pass

    def visit_function_type(self, node: 'FunctionTypeNode'):
        for parameter in node.parameter_types:
            parameter.accept(self)
            node.invalid = node.invalid or parameter.invalid
        node.return_type.accept(self)
        node.invalid = node.invalid or node.return_type.invalid


class ScopedVisitor(AbstractVisitor, ABC):
    def __init__(self, module: Module):
        self.module = module
        self.globals = module.globals
        self.scope = module.globals

    def visit_program(self, node: 'ProgramNode'):
        assert node.chunk.symbol_table and node.chunk.symbol_table.parent == self.globals, 'fatal: global scope mismatch'
        super().visit_program(node)

    def visit_chunk(self, node: 'ChunkNode'):
        assert node.symbol_table and node.symbol_table.parent == self.scope, 'fatal: scope parent mismatch'
        scope = self.scope
        self.scope = node.get_symbol_table()
        super().visit_chunk(node)
        self.scope = scope
