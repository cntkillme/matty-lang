from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from mattylang.ast import *


class AbstractVisitor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def visit_program(self, node: 'ProgramNode'):
        self.visit_chunk(node.chunk)

    def visit_chunk(self, node: 'ChunkNode'):
        for statement in node.statements:
            statement.accept(self)

    def visit_variable_definition(self, node: 'VariableDefinitionNode'):
        node.identifier.accept(self)
        node.initializer.accept(self)

    def visit_variable_assignment(self, node: 'VariableAssignmentNode'):
        node.identifier.accept(self)
        node.value.accept(self)

    def visit_if_statement(self, node: 'IfStatementNode'):
        node.condition.accept(self)
        node.if_body.accept(self)

        if node.else_body is not None:
            node.else_body.accept(self)

    def visit_while_statement(self, node: 'WhileStatementNode'):
        node.condition.accept(self)
        node.body.accept(self)

    def visit_break_statement(self, node: 'BreakStatementNode'):
        pass

    def visit_continue_statement(self, node: 'ContinueStatementNode'):
        pass

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        node.identifier.accept(self)
        for parameter in node.parameters:
            parameter.accept(self)
        node.body.accept(self)

    def visit_function_parameter(self, node: 'FunctionParameterNode'):
        node.identifier.accept(self)
        node.type.accept(self)

    def visit_return_statement(self, node: 'ReturnStatementNode'):
        if node.value is not None:
            node.value.accept(self)

    def visit_call_statement(self, node: 'CallStatementNode'):
        node.call_expression.accept(self)

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
        for argument in node.arguments:
            argument.accept(self)

    def visit_unary_expression(self, node: 'UnaryExpressionNode'):
        node.operand.accept(self)

    def visit_binary_expression(self, node: 'BinaryExpressionNode'):
        node.left.accept(self)
        node.right.accept(self)

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
        node.return_type.accept(self)
