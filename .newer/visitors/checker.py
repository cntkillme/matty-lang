from compiler.nodes import *
from compiler.scope import Scope
from compiler.visitor import AbstractVisitor


class Checker(AbstractVisitor):
    def __init__(self):
        self.__active_scope: Scope = Scope()

    @staticmethod
    def is_type_equal(left: TypeNode, right: TypeNode):
        return isinstance(left, right.__class__) and isinstance(right, left.__class__)

    def visit_program(self, program: ProgramNode) -> None:
        scope = program.get_chunk().get_scope()
        assert scope is not None, 'fatal: program has no scope, was the bind step skipped?'
        self.__active_scope = scope
        self.visit_chunk(program.get_chunk())

    def visit_chunk(self, chunk: ChunkNode):
        scope = chunk.get_scope()
        assert scope is not None, 'fatal: chunk has no scope, was the bind step skipped?'
        self.__active_scope = scope
        for statement in chunk.get_statements():
            self.visit_statement(statement)
        parent = self.__active_scope.get_parent()
        assert parent is not None, 'fatal: scope has no parent, was the bind step skipped?'
        self.__active_scope = parent

    def visit_variable_definition(self, variable_definition: VariableDefinitionNode):
        name, value = variable_definition.get_name(), variable_definition.get_value()
        self.visit_expression(value)
        value_type = value.get_type()
        assert value_type is not None, 'fatal: value node is untyped'
        name.set_type(value_type)

    def visit_variable_assignment(self, variable_assignment: VariableAssignmentNode):
        name, value = variable_assignment.get_name(), variable_assignment.get_value()

        if name.is_forward_reference():
            raise ValueError('could not assign to a variable before it was defined')

        self.visit_identifier(name)
        self.visit_expression(value)
        name_type, value_type = name.get_type(), value.get_type()
        assert name_type is not None, 'fatal: name node is untyped'
        assert value_type is not None, 'fatal: value node is untyped'

        if not self.is_type_equal(name_type, value_type):
            raise ValueError('the types of the variable and value are incompatible',
                             name.get_text(), name.get_type(), value.get_type())

    def visit_unary_expression(self, unary_expression: UnaryExpressionNode):
        operator, operand = unary_expression.get_operator(), unary_expression.get_operand()
        self.visit_expression(operand)
        expr_type = operand.get_type()
        assert expr_type is not None, 'fatal: expression is untyped'

        if operator == '-':
            if not isinstance(expr_type, RealTypeNode):
                raise ValueError('the operand of negation must be a real')
        elif operator == '!':
            if not isinstance(expr_type, BoolTypeNode):
                raise ValueError('the operand of logical negation must be a boolean')
            else:
                raise ValueError('invalid operand type for unary minus', expr_type)
        unary_expression.set_type(expr_type)

    def visit_binary_expression(self, binary_expression: BinaryExpressionNode):
        operator, left, right = binary_expression.get_operator(), binary_expression.get_left(), binary_expression.get_right()
        self.visit_expression(left)
        self.visit_expression(right)
        left_type = left.get_type()
        right_type = right.get_type()

        assert left_type is not None, 'fatal: left expression is untyped'
        assert right_type is not None, 'fatal: right expression is untyped'

        if not self.is_type_equal(left_type, right_type):
            raise ValueError('the types of the left and right expressions are incompatible', left_type, right_type)

        if operator in {'+', '-', '*', '/', '%'}:
            if not isinstance(left_type, RealTypeNode):
                raise ValueError('expected left expression to be real', left_type)
            elif not isinstance(right_type, RealTypeNode):
                raise ValueError('expected right expression to be real', right_type)
        elif operator in {'<', '>', '<=', '>='}:
            if not isinstance(left_type, RealTypeNode) and not isinstance(left_type, StringTypeNode):
                raise ValueError('expected left expression to be real or string', left_type)
            elif not isinstance(right_type, BoolTypeNode) and not isinstance(right_type, StringTypeNode):
                raise ValueError('expected right expression to be real or string', right_type)

        binary_expression.set_type(left_type)

    def visit_nil_literal(self, nil_literal: NilLiteralNode):
        nil_literal.set_type(nil_type_instance)

    def visit_bool_literal(self, bool_literal: BoolLiteralNode):
        bool_literal.set_type(bool_type_instance)

    def visit_real_literal(self, real_literal: RealLiteralNode):
        real_literal.set_type(real_type_instance)

    def visit_string_literal(self, string_literal: StringLiteralNode):
        string_literal.set_type(string_type_instance)

    def visit_identifier(self, identifier: IdentifierNode):
        symbol = identifier.get_symbol()
        assert symbol is not None, f'fatal: identifier {identifier.get_text()} has no symbol, was the bind step skipped?'
        declaration = symbol.get_value_declaration()
        assert declaration is not None, f'fatal: identifier {identifier.get_text()} has no declaration, was the bind step skipped?'
        value_type = declaration.get_value().get_type()
        if value_type is not None:
            identifier.set_type(value_type)
        else:
            raise ValueError('undeclared identifier', identifier.get_text())


nil_type_instance = NilTypeNode()
bool_type_instance = BoolTypeNode()
real_type_instance = RealTypeNode()
string_type_instance = StringTypeNode()
