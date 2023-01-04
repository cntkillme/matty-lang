from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import ScopedVisitor


class Checker(ScopedVisitor):
    def __init__(self, module: Module):
        super().__init__(module)

    def is_equivalent(self, left: TypeNode, right: TypeNode):
        if left is None or right is None:
            return False
        return left.is_equivalent(right)

    def visit_program(self, node: ProgramNode):
        super().visit_program(node)
        node.invalid = node.invalid or node.chunk.invalid

    def visit_chunk(self, node: ChunkNode):
        for statement in node.statements:
            statement.accept(self)
            node.invalid = node.invalid or statement.invalid

    def visit_variable_definition(self, node: VariableDefinitionNode):
        node.initializer.accept(self)

        if node.identifier.symbol is not None:
            node.identifier.symbol.type = node.initializer.type

        node.identifier.accept(self)
        node.invalid = node.invalid or node.identifier.invalid or node.initializer.invalid

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        super().visit_variable_assignment(node)  # visit children

        # diagnostic: missing type
        # Another diagnostic should have been emitted for if it has no type.
        identifier_type, value_type = node.identifier.type, node.value.type
        if identifier_type is None or value_type is None:
            node.invalid = True
            return

        # diagnostic: incompatible types
        if identifier_type is None or value_type is None or not identifier_type.is_equivalent(value_type):
            node.invalid = True
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible types for assignment: {identifier_type} = {value_type}', node.position)
            return

        node.invalid = node.invalid or node.identifier.invalid or node.value.invalid

    def visit_unary_expression(self, node: UnaryExpressionNode):
        super().visit_unary_expression(node)  # visit children
        operator, value_type = node.operator, node.operand.type
        if value_type is None:
            node.invalid = True
            return

        if operator == '-':
            # diagnostic: incompatible operand type
            if not value_type.is_equivalent(RealTypeNode()):
                node.invalid = True
                self.module.diagnostics.emit_diagnostic(
                    'error', f'analysis: incompatible operand type for expression: {operator}{value_type}', node.position)
                return

            node.type = value_type
        elif operator == '!':
            # diagnostic: incompatible operand type
            if not value_type.is_equivalent(BoolTypeNode()):
                node.invalid = True
                self.module.diagnostics.emit_diagnostic(
                    'error', f'analysis: incompatible operand type for expression: {operator}{value_type}', node.position)
                return

            node.type = BoolTypeNode()
        else:
            assert False, f'unary operator {operator} is invalid'  # lexer invariant: all unary operators are valid

    def visit_binary_expression(self, node: BinaryExpressionNode):
        super().visit_binary_expression(node)  # visit children
        operator = node.operator
        left, right = node.left, node.right
        left_type, right_type = left.type, right.type

        # diagnostic: missing type
        # Another diagnostic should have been emitted for if it has no type.
        if left_type is None or right_type is None:
            node.invalid = True
            return

        node.invalid = node.invalid or left.invalid or right.invalid or left_type.invalid or right_type.invalid
        type_error = left_type is None or right_type is None or not left_type.is_equivalent(right_type)
        result_type = left_type

        if operator == '+':
            result_type = left_type
            type_error = type_error or not (left_type.is_equivalent(RealTypeNode())
                                            or left_type.is_equivalent(StringTypeNode()))
        elif operator in {'-', '*', '/', '%'}:
            result_type = left_type
            type_error = type_error or not left_type.is_equivalent(RealTypeNode())
        elif operator in {'==', '!='}:
            result_type = BoolTypeNode()
        elif operator in {'<', '<=', '>', '>='}:
            result_type = BoolTypeNode()
            type_error = type_error or not left_type.is_three_way_comparable()
        elif operator in {'||', '&&'}:
            result_type = BoolTypeNode()
            type_error = type_error or not left_type.is_equivalent(BoolTypeNode())
        else:
            assert False, f'binary operator {operator} is invalid'  # lexer invariant: all binary operators are valid

        if type_error:
            # diagnostic: incompatible operand types
            node.invalid = True
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible operand types for expression: {left_type} {operator} {right_type}', node.position)
            return

        node.type = result_type

    def visit_nil_literal(self, node: NilLiteralNode):
        node.type = NilTypeNode()

    def visit_bool_literal(self, node: BoolLiteralNode):
        node.type = BoolTypeNode()

    def visit_real_literal(self, node: RealLiteralNode):
        node.type = RealTypeNode()

    def visit_string_literal(self, node: StringLiteralNode):
        node.type = StringTypeNode()

    def visit_identifier(self, node: IdentifierNode):
        symbol = node.symbol
        if symbol is not None:
            node.type = symbol.type
