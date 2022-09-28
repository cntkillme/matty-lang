from compiler.nodes import *
from compiler.visitor import AbstractVisitor


class AstPrinter(AbstractVisitor):
    def __init__(self, indent: int = 0):
        self.__indent = indent

    def __write(self, text: str):
        print('  ' * self.__indent + text)

    def visit_program(self, program: ProgramNode):
        self.__write(program.get_kind())
        self.__indent += 1
        self.visit_chunk(program.get_chunk())
        self.__indent -= 1

    def visit_chunk(self, chunk: ChunkNode):
        self.__write(chunk.get_kind())
        self.__indent += 1
        for statement in chunk.get_statements():
            self.visit_statement(statement)
        self.__indent -= 1

    def visit_variable_definition(self, variable_definition: VariableDefinitionNode):
        self.__write(variable_definition.get_kind())
        self.__indent += 1
        self.visit_identifier(variable_definition.get_name())
        self.visit_expression(variable_definition.get_value())
        self.__indent -= 1

    def visit_variable_assignment(self, variable_assignment: VariableAssignmentNode):
        self.__write(variable_assignment.get_kind())
        self.__indent += 1
        self.visit_identifier(variable_assignment.get_name())
        self.visit_expression(variable_assignment.get_value())
        self.__indent -= 1

    def visit_expression(self, expression: ExpressionNode):
        expression_type = expression.get_type()
        super().visit_expression(expression)
        if expression_type is not None:
            self.__indent += 1
            self.__write(f'type({expression_type})')
            self.__indent -= 1

    def visit_unary_expression(self, unary_expression: UnaryExpressionNode):
        self.__write(
            f'{unary_expression.get_kind()}({unary_expression.get_operator()})')
        self.__indent += 1
        self.visit_expression(unary_expression.get_operand())
        self.__indent -= 1

    def visit_binary_expression(self, binary_expression: BinaryExpressionNode):
        self.__write(
            f'{binary_expression.get_kind()}({binary_expression.get_operator()})')

        self.__indent += 1
        self.visit_expression(binary_expression.get_left())
        self.visit_expression(binary_expression.get_right())
        self.__indent -= 1

    def visit_nil_literal(self, nil_literal: NilLiteralNode):
        self.__write(f'{nil_literal.get_kind()}(nil)')

    def visit_bool_literal(self, bool_literal: BoolLiteralNode):
        self.__write(f'{bool_literal.get_kind()}({bool_literal.get_value()})')

    def visit_real_literal(self, real_literal: RealLiteralNode):
        self.__write(f'{real_literal.get_kind()}({real_literal.get_value()})')

    def visit_string_literal(self, string_literal: StringLiteralNode):
        self.__write(
            f'{string_literal.get_kind()}({repr(string_literal.get_value())})')

    def visit_identifier(self, identifier: IdentifierNode):
        self.__write(f'{identifier.get_kind()}({identifier.get_text()})')
        symbol = identifier.get_symbol()
        if symbol is not None:
            self.__indent += 1
            self.__write(f'symbol({symbol})')
            self.__indent -= 1


class SymbolPrinter(AbstractVisitor):
    def __init__(self, indent: int = 0):
        self.__indent = indent

    def __write(self, text: str):
        print('  ' * self.__indent + text)

    def visit_chunk(self, chunk: ChunkNode):
        self.__write('{')
        self.__indent += 1
        scope = chunk.get_scope()
        assert scope is not None

        for text, symbol in scope.get_symbols().items():
            self.__write(f'{text} = {symbol.get_value_declaration()}')

        for statement in chunk.get_statements():
            self.visit_statement(statement)

        self.__indent -= 1
        self.__write('}')
