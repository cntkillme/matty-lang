from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import AbstractVisitor


class Checker(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module
        self.__enclosed_loop_statement: Optional[WhileStatementNode] = None
        self.__enclosed_function_definition: Optional[FunctionDefinitionNode] = None

    def is_equivalent(self, left: TypeNode, right: TypeNode):
        if left is None or right is None:
            return False
        return left.is_equivalent(right)

    def visit_variable_definition(self, node: VariableDefinitionNode):
        node.initializer.accept(self)

        if node.identifier.symbol is None:
            return

        node.identifier.symbol.type = node.initializer.type
        node.identifier.accept(self)

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        super().visit_variable_assignment(node)  # visit children
        node.identifier.type = node.value.type
        identifier_type, value_type = node.identifier.type, node.value.type

        # Another diagnostic should have been emitted if it has no type.
        if identifier_type is None or value_type is None:
            return

        if identifier_type is None or value_type is None or not identifier_type.is_equivalent(value_type):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible types for assignment: {identifier_type} = {value_type}', node.position)
            return

    def visit_if_statement(self, node: 'IfStatementNode'):
        super().visit_if_statement(node)  # visit children
        condition_type = node.condition.type

        # Another diagnostic should have been emitted if it has no type.
        if condition_type is None:
            return

        if not condition_type.is_equivalent(BoolTypeNode()):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: expected type of condition to be Bool (got {condition_type})', node.condition.position)
            return

    def visit_while_statement(self, node: 'WhileStatementNode'):
        last_loop_stmt = self.__enclosed_loop_statement
        self.__enclosed_loop_statement = node
        super().visit_while_statement(node)  # visit children
        self.__enclosed_loop_statement = last_loop_stmt
        condition_type = node.condition.type

        # Another diagnostic should have been emitted if it has no type.
        if condition_type is None:
            return

        if not condition_type.is_equivalent(BoolTypeNode()):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: expected type of condition to be Bool (got {condition_type})', node.condition.position)
            return

    def visit_break_statement(self, node: BreakStatementNode):
        if self.__enclosed_loop_statement is None:
            self.module.diagnostics.emit_diagnostic(
                'error', 'analysis: break statement outside of loop', node.position)

    def visit_continue_statement(self, node: ContinueStatementNode):
        if self.__enclosed_loop_statement is None:
            self.module.diagnostics.emit_diagnostic(
                'error', 'analysis: continue statement outside of loop', node.position)

    def visit_unary_expression(self, node: UnaryExpressionNode):
        super().visit_unary_expression(node)  # visit children
        operator, value_type = node.operator, node.operand.type
        if value_type is None:
            return

        if operator == '-':
            if not value_type.is_equivalent(RealTypeNode()):
                self.module.diagnostics.emit_diagnostic(
                    'error', f'analysis: incompatible operand type for expression: {operator}{value_type}', node.position)
                return

            node.type = value_type
        elif operator == '!':
            if not value_type.is_equivalent(BoolTypeNode()):
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

        # Another diagnostic should have been emitted for if it has no type.
        if left_type is None or right_type is None:
            return

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
