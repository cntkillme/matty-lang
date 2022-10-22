from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import ScopedVisitor


class Checker(ScopedVisitor):
    def __init__(self, module: Module):
        super().__init__(module)

    def visit_program(self, node: 'ProgramNode'):
        super().visit_program(node)
        node.invalid = node.invalid or node.chunk.invalid

    def visit_chunk(self, node: ChunkNode):
        for statement in node.statements:
            statement.accept(self)
            node.invalid = node.invalid or statement.invalid

    def visit_variable_definition(self, node: VariableDefinitionNode):
        node.initializer.accept(self)
        node.identifier.type = node.initializer.type
        node.identifier.accept(self)

        # diagnostic: incompatible types
        if node.identifier.type is None:
            node.invalid = True
            return

        node.invalid = node.invalid or node.identifier.invalid or node.initializer.invalid

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        super().visit_variable_assignment(node)  # visit children

        # diagnostic: variable is constant
        symbol = node.identifier.symbol
        if symbol is not None:
            if symbol.declaration.constant:
                node.invalid = True
                self.module.diagnostics.emit_error(
                    f'variable {node.identifier.value} is constant', *node.get_location())
                return

        # diagnostic: incompatible types
        identifier_type, value_type = node.identifier.type, node.value.type
        if identifier_type is None or value_type is None or not identifier_type.is_equivalent(value_type):
            node.invalid = True
            self.module.diagnostics.emit_error(
                f'incompatible types for assignment: {identifier_type} = {value_type}', *node.get_location())
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
                self.module.diagnostics.emit_error(
                    f'incompatible operand type for expression: {operator}{value_type}', *node.get_location())
                return

            node.type = value_type
        elif operator == '!':
            # diagnostic: incompatible operand type
            if not value_type.is_equivalent(BoolTypeNode()):
                node.invalid = True
                self.module.diagnostics.emit_error(
                    f'incompatible operand type for expression: {operator}{value_type}', *node.get_location())
                return

            node.type = BoolTypeNode()
        else:
            assert False, f'unary operator {operator} is invalid'  # lexer invariant: all unary operators are valid

    def visit_binary_expression(self, node: BinaryExpressionNode):
        super().visit_binary_expression(node)  # visit children
        operator = node.operator
        left, right = node.left, node.right
        left_type, right_type = left.type, right.type

        if left_type is None or right_type is None:
            self.module.diagnostics.emit_error(
                f'incompatible operand types for expression: {left_type} {operator} {right_type}', *node.get_location())
            node.invalid = True
            return

        node.invalid = node.invalid or left.invalid or right.invalid or left_type.invalid or right_type.invalid

        if operator in {'+', '-', '*', '/', '%'}:
            # diagnostic: incompatible operand types (implicit conversion is a non-goal)
            if not left_type.is_equivalent(right_type):
                node.invalid = True
                self.module.diagnostics.emit_error(
                    f'incompatible operand types for expression: {left_type} {operator} {right_type}', *node.get_location())
                return

            node.type = left_type
        elif operator in {'==', '!='}:
            node.type = BoolTypeNode()
        elif operator in {'<', '<=', '>', '>='}:
            # diagnostic: incompatible operand types
            if not (left_type.is_equivalent(right_type) and left_type.is_three_way_comparable() and right_type.is_three_way_comparable()):
                node.invalid = True
                self.module.diagnostics.emit_error(
                    f'incompatible operand types for expression: {left_type} {operator} {right_type}', *node.get_location())
                return

            node.type = BoolTypeNode()
        elif operator in {'||', '&&'}:
            # diagnostic: incompatible operand types
            if not (left_type.is_equivalent(BoolTypeNode()) and right_type.is_equivalent(BoolTypeNode())):
                node.invalid = True
                self.module.diagnostics.emit_error(
                    f'incompatible operands types for expression: {left_type} {operator} {right_type}', *node.get_location())
                return

            node.type = BoolTypeNode()
        else:
            assert False, f'binary operator {operator} is invalid'  # lexer invariant: all binary operators are valid

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
            node.type = symbol.declaration.identifier.type
            node.invalid = node.invalid or (node.type is None or node.type.invalid)
        else:
            node.invalid = True
