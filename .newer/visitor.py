from abc import ABC
from compiler.nodes import *


class AbstractVisitor(ABC):
    def visit_program(self, program: ProgramNode):
        self.visit_chunk(program.get_chunk())

    def visit_chunk(self, chunk: ChunkNode):
        for statement in chunk.get_statements():
            self.visit_statement(statement)

    def visit_statement(self, statement: StatementNode):
        if isinstance(statement, ChunkNode):
            self.visit_chunk(statement)
        elif isinstance(statement, VariableDefinitionNode):
            self.visit_variable_definition(statement)
        elif isinstance(statement, VariableAssignmentNode):
            self.visit_variable_assignment(statement)
        else:
            raise ValueError('unknown statement kind', statement.get_kind())

    def visit_variable_definition(self, variable_definition: VariableDefinitionNode):
        self.visit_identifier(variable_definition.get_name())
        self.visit_expression(variable_definition.get_value())

    def visit_variable_assignment(self, variable_assignment: VariableAssignmentNode):
        self.visit_identifier(variable_assignment.get_name())
        self.visit_expression(variable_assignment.get_value())

    def visit_expression(self, expression: ExpressionNode):
        if isinstance(expression, PrimaryExpressionNode):
            self.visit_primary_expression(expression)
        elif isinstance(expression, UnaryExpressionNode):
            self.visit_unary_expression(expression)
        elif isinstance(expression, BinaryExpressionNode):
            self.visit_binary_expression(expression)
        else:
            raise ValueError('unknown expression kind', expression.get_kind())

    def visit_primary_expression(self, primary_expression: PrimaryExpressionNode):
        if isinstance(primary_expression, NilLiteralNode):
            self.visit_nil_literal(primary_expression)
        elif isinstance(primary_expression, BoolLiteralNode):
            self.visit_bool_literal(primary_expression)
        elif isinstance(primary_expression, RealLiteralNode):
            self.visit_real_literal(primary_expression)
        elif isinstance(primary_expression, StringLiteralNode):
            self.visit_string_literal(primary_expression)
        elif isinstance(primary_expression, IdentifierNode):
            self.visit_identifier(primary_expression)
        else:
            raise ValueError('unknown primary expression kind', primary_expression.get_kind())

    def visit_unary_expression(self, unary_expression: UnaryExpressionNode):
        self.visit_expression(unary_expression.get_operand())

    def visit_binary_expression(self, binary_expression: BinaryExpressionNode):
        self.visit_expression(binary_expression.get_left())
        self.visit_expression(binary_expression.get_right())

    def visit_nil_literal(self, nil_literal: NilLiteralNode):
        pass

    def visit_bool_literal(self, bool_literal: BoolLiteralNode):
        pass

    def visit_real_literal(self, real_literal: RealLiteralNode):
        pass

    def visit_string_literal(self, string_literal: StringLiteralNode):
        pass

    def visit_identifier(self, identifier: IdentifierNode):
        pass
