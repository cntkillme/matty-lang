from mattylang.ast import *
from mattylang.module import Module
from mattylang.visitor import AbstractVisitor


class Checker(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module

    def visit_variable_definition(self, node: VariableDefinitionNode):
        node.initializer.accept(self)

        if node.identifier.symbol is None:
            return

        # type inference: type of variable = type of initializer
        node.identifier.symbol.type = node.initializer.type
        node.identifier.accept(self)

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        super().visit_variable_assignment(node)  # visit children
        node.identifier.type = node.value.type
        identifier_type, value_type = node.identifier.type, node.value.type

        if identifier_type is None or value_type is None:
            return

        if not value_type.is_assignable_to(identifier_type):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible types for assignment: {identifier_type} = {value_type}', node.position)
            return

    def visit_if_statement(self, node: IfStatementNode):
        node.condition.accept(self)
        condition_type = node.condition.type

        if condition_type is not None and not condition_type.is_equivalent(BoolTypeNode()):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: expected type of condition to be Bool (got {condition_type})', node.condition.position)
            return

        node.if_body.accept(self)
        if node.else_body is not None:
            node.else_body.accept(self)

    def visit_while_statement(self, node: WhileStatementNode):
        node.condition.accept(self)
        condition_type = node.condition.type

        if condition_type is not None and not condition_type.is_equivalent(BoolTypeNode()):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: expected type of condition to be Bool (got {condition_type})', node.condition.position)
            return

        node.body.accept(self)

    def visit_break_statement(self, node: BreakStatementNode):
        if node.get_enclosing_loop_statement() is None:
            self.module.diagnostics.emit_diagnostic(
                'error', 'analysis: break statement outside of loop', node.position)

    def visit_continue_statement(self, node: ContinueStatementNode):
        if node.get_enclosing_loop_statement() is None:
            self.module.diagnostics.emit_diagnostic(
                'error', 'analysis: continue statement outside of loop', node.position)

    def visit_function_definition(self, node: FunctionDefinitionNode):
        super().visit_function_definition(node)  # visit children

    def visit_function_parameter(self, node: FunctionParameterNode):
        super().visit_function_parameter(node)  # visit children

    def visit_return_statement(self, node: ReturnStatementNode):
        super().visit_return_statement(node)  # visit children
        enclosing_function = node.get_enclosing_function_definition()

        if enclosing_function is None:
            self.module.diagnostics.emit_diagnostic(
                'error', 'analysis: return statement outside of function', node.position)
            return

        return_type = node.value.type or NilTypeNode() if node.value is not None else NilTypeNode()
        chunk_type = enclosing_function.body.return_type

        if chunk_type is not None and not return_type.is_assignable_to(chunk_type):
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible return type {return_type}, expected {chunk_type}', return_type.position)
            return
        elif chunk_type is None:
            enclosing_function.body.return_type = return_type

    def visit_nil_literal(self, node: NilLiteralNode):
        node.type = NilTypeNode()

    def visit_bool_literal(self, node: BoolLiteralNode):
        node.type = BoolTypeNode()

    def visit_real_literal(self, node: RealLiteralNode):
        node.type = RealTypeNode()

    def visit_string_literal(self, node: StringLiteralNode):
        node.type = StringTypeNode()

    def visit_identifier(self, node: IdentifierNode):
        if node.symbol is not None:
            node.type = node.symbol.type

    def visit_call_expression(self, node: CallExpressionNode):
        parameter_types: List[TypeNode] = []
        for argument in node.arguments:
            argument.accept(self)
            parameter_types.append(argument.type or AnyTypeNode())
        #

        return super().visit_call_expression(node)  # visit children

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

        type_error = left_type.is_equivalent(right_type)
        result_type = left_type

        if operator == '+':
            result_type = left_type
            type_error = type_error or not (left_type.is_assignable_to(RealTypeNode())
                                            or left_type.is_assignable_to(StringTypeNode()))
        elif operator in {'-', '*', '/', '%'}:
            result_type = left_type
            type_error = type_error or not left_type.is_assignable_to(RealTypeNode())
        elif operator in {'==', '!='}:
            result_type = BoolTypeNode()
        elif operator in {'<', '<=', '>', '>='}:
            result_type = BoolTypeNode()
            type_error = type_error or not (left_type.is_assignable_to(RealTypeNode())
                                            or left_type.is_assignable_to(StringTypeNode()))
        elif operator in {'||', '&&'}:
            result_type = BoolTypeNode()
            type_error = type_error or not left_type.is_assignable_to(BoolTypeNode())
        else:
            assert False, f'binary operator {operator} is invalid'  # lexer invariant: all binary operators are valid

        if type_error:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: incompatible operand types for expression: {left_type} {operator} {right_type}', node.position)
            return

        node.type = result_type
