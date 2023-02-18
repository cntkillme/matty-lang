from mattylang.ast import *
from mattylang.lexer import Lexer


class Parser:
    def __init__(self, lexer: Lexer):
        self.module = lexer.module
        self.lexer = lexer
        self.__program: Optional[ProgramNode] = None

    def reset(self):
        self.lexer.reset()
        self.__program = None

    def parse(self) -> ProgramNode:
        if self.__program is None:
            self.__program = self.__parse_program()
            self.__expect('eof', 'to end program')
        return self.__program

    __unary_operators = {'!': True, '-': True}

    __binary_operators = {  # precedence levels
        '&&': 1, '||': 1,
        '<': 2, '>': 2, '<=': 2, '>=': 2, '==': 2, '!=': 2,
        '+': 3, '-': 3,
        '*': 4, '/': 4, '%': 4,
    }

    def __parse_program(self) -> ProgramNode:
        start = self.lexer.position
        return ProgramNode(self.__parse_chunk(terminator='eof', start=start), position=start)

    def __parse_statement(self) -> Optional[StatementNode]:
        token = self.lexer.peek()
        start = token.position
        if token.kind == '{':  # chunk
            self.lexer.scan()
            chunk = self.__parse_chunk(terminator='}', start=start)
            self.__expect('}', 'to close block')
            return chunk
        elif token.kind == 'def':  # variable/function definition
            token = self.lexer.scan()  # skip 'def'
            identifier = self.__parse_identifier()

            if identifier.value == '#invalid':
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected identifier for definition, got {token}', token.position)

            token2 = self.lexer.peek()
            if token2.kind == '=':  # variable definition
                return self.__parse_variable_definition(identifier, start=start)
            elif token2.kind == '(':  # function definition
                return self.__parse_function_definition(identifier, start=start)
            else:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected = or ( for definition, got {token2}', token2.position)
                return None
        elif token.kind == 'if':  # if statement
            return self.__parse_if_statement()
        elif token.kind == 'while':  # while statement
            return self.__parse_while_statement()
        elif token.kind == 'break':  # break statement
            self.lexer.scan()
            return BreakStatementNode(position=token.position)
        elif token.kind == 'continue':  # continue statement
            self.lexer.scan()
            return ContinueStatementNode(position=token.position)
        elif token.kind == 'return':  # return statement
            self.lexer.scan()
            return ReturnStatementNode(self.__parse_expression(), position=token.position)
        elif token.kind == 'identifier':  # variable assignment or call expression
            identifier = IdentifierNode(token.lexeme, position=token.position)
            token = self.lexer.scan()

            if token.kind == '=':  # variable assignment
                return self.__parse_variable_assignment(identifier)
            elif token.kind == '(':  # call statement
                call_expression = self.__parse_call_expression(identifier)
                return CallStatementNode(call_expression, position=call_expression.position)
            else:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {identifier}', identifier.position)
                return None
        else:
            # parse expression as temporaries, to provide more meaningful diagnostics.
            expression = self.__parse_expression()
            if expression is None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected statement, got {token}', token.position)
                self.lexer.scan()  # skip non-statement/expression token
            else:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {expression}', expression.position)
                return VariableDefinitionNode(IdentifierNode('#invalid'), expression)

    def __parse_chunk(self, terminator: str, start: int):
        statements: List[StatementNode] = []
        token = self.lexer.peek()

        while token.kind != 'eof' and token.kind != terminator:
            statement = self.__parse_statement()
            if statement is not None:
                statements.append(statement)
            token = self.lexer.peek()

        return ChunkNode(statements, position=start)

    def __parse_variable_definition(self, identifier: IdentifierNode, start: int):
        self.lexer.scan()  # skip '='
        initializer = self.__expect_expression(f'to initialize variable {identifier.value}') or NilLiteralNode()
        return VariableDefinitionNode(identifier, initializer, position=start)

    def __parse_variable_assignment(self, identifier: IdentifierNode):
        self.lexer.scan()  # skip '='
        initializer = self.__expect_expression(f'to assign variable {identifier.value}') or NilLiteralNode()
        return VariableAssignmentNode(identifier, initializer, position=identifier.position)

    def __parse_if_statement(self):
        start = self.lexer.peek().position
        self.lexer.scan()  # skip 'if'
        self.__expect('(', 'to open if condition')
        if_condition = self.__expect_expression('after (') or BoolLiteralNode(False)
        self.__expect(')', 'to close if condition')
        if_body = self.__expect_statement('after )') or ChunkNode()
        else_body = None

        if self.lexer.peek().kind == 'else':
            self.lexer.scan()
            else_body = self.__expect_statement('after else') or ChunkNode()

        # transform non-chunk statement into chunk
        if not isinstance(if_body, ChunkNode):
            if_body = ChunkNode([if_body], position=if_body.position)

        # transform non-chunk statement into chunk
        if else_body is not None and not isinstance(else_body, ChunkNode):
            else_body = ChunkNode([else_body], position=else_body.position)

        return IfStatementNode(if_condition, if_body, else_body, position=start)

    def __parse_while_statement(self):
        start = self.lexer.peek().position
        self.__expect('(', 'to open while condition')
        condition = self.__expect_expression('after while') or BoolLiteralNode(False)
        self.__expect(')', 'to close while condition')
        body = self.__expect_statement('after while') or ChunkNode()

        # transform non-chunk statement chunk
        if not isinstance(body, ChunkNode):
            body = ChunkNode([body], position=body.position)

        return WhileStatementNode(condition, body, position=start)

    def __parse_function_definition(self, identifier: IdentifierNode, start: int):
        self.__expect('(', 'to specify function parameters')
        parameters = self.__parse_parameter_list()
        self.__expect(')', 'to close function parameters')

        position = self.lexer.peek().position
        if self.__expect('{', 'to open function body'):
            body = self.__parse_chunk(terminator='}', start=position)
            self.__expect('}', 'to close function body')
        else:
            body = ChunkNode()

        return FunctionDefinitionNode(identifier, parameters, body, position=start)

    def __parse_function_parameter(self, identifier: IdentifierNode):
        self.__expect(':', 'to specify parameter type')
        type = self.__expect_type('to specify parameter type') or AnyTypeNode()
        return FunctionParameterNode(identifier, type, position=identifier.position)

    def __parse_parameter_list(self):
        parameters: List[FunctionParameterNode] = []
        token = self.lexer.peek()

        while token.kind != ')' and token.kind != 'eof':
            identifier = self.__parse_identifier()

            if identifier.value != '#invalid;':
                parameters.append(self.__parse_function_parameter(identifier))
                token = self.lexer.peek()

            if token.kind == ',':
                self.lexer.scan()
            elif token.kind != ')':
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {token} in parameter list', token.position)
                self.lexer.scan()  # skip non-parameter token

            token = self.lexer.peek()

        return parameters

    def __parse_expression(self) -> ExpressionNode | None:
        return self.__parse_binary_expression(0)

    def __parse_primary_expression(self) -> ExpressionNode | None:
        token = self.lexer.peek()

        if token.kind == '(':
            self.lexer.scan()
            expression = self.__parse_expression()
            self.__expect(')', 'to close expression')
            return expression

        if token.kind == 'nil':
            self.lexer.scan()
            return NilLiteralNode(position=token.position)
        elif token.kind == 'true':
            self.lexer.scan()
            return BoolLiteralNode(True, position=token.position)
        elif token.kind == 'false':
            self.lexer.scan()
            return BoolLiteralNode(False, position=token.position)
        elif token.kind == 'real_literal':
            self.lexer.scan()
            try:
                # lexer invariant: token.lexeme is a valid float
                return RealLiteralNode(float(token.lexeme), position=token.position)
            except ValueError:
                assert False, f'invalid real literal {token.lexeme}'
        elif token.kind == 'string_literal':
            self.lexer.scan()
            return StringLiteralNode(token.lexeme, position=token.position)
        elif token.kind == 'identifier':  # identifier or function call
            identifier = self.__parse_identifier()

            if self.lexer.peek().kind == '(':  # function call
                return self.__parse_call_expression(identifier)
            else:
                return identifier
        else:
            return None

    def __parse_identifier(self) -> IdentifierNode:
        token = self.lexer.peek()
        if token.kind == 'identifier':
            node = IdentifierNode(token.lexeme, position=token.position)
            self.lexer.scan()
            return node
        else:
            return IdentifierNode('#error', position=token.position)

    def __parse_call_expression(self, identifier: IdentifierNode) -> CallExpressionNode:
        self.__expect('(', 'to open function arguments')
        arguments = self.__parse_expression_list()
        self.__expect(')', 'to close function arguments')
        node = CallExpressionNode(identifier, arguments)
        node.position = identifier.position
        return node

    def __parse_unary_expression(self) -> ExpressionNode | None:
        operator = self.lexer.peek()

        if operator.kind in self.__unary_operators:
            self.lexer.scan()  # skip operator
            operand = self.__parse_unary_expression()
            next_token = self.lexer.peek()

            if operand is None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression after {operator} (got {next_token})', next_token.position)
                return None

            expr = UnaryExpressionNode(operator.kind, operand)
            expr.position = operator.position
            return expr
        else:
            return self.__parse_primary_expression()

    def __parse_binary_expression(self, precedence: int) -> ExpressionNode | None:
        left = self.__parse_unary_expression()
        operator = self.lexer.peek()

        # Keep parsing expressions at or greater precedence of the current operator.
        # Example: `1 + 2 - 3` will be parsed as `(1 + 2) - 3`
        while left is not None and self.__binary_operators.get(operator.kind, -1) >= precedence:
            token = self.lexer.peek()
            next_token = self.lexer.scan()  # skip operator

            # Parse sub-expressions of right operand with higher precedence than the current operator.
            # Example: `1 + 2 * 3` will be parsed as `1 + (2 * 3)`
            right = self.__parse_binary_expression(self.__binary_operators[operator.kind] + 1)

            if not right:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression (got {next_token}) after {token}', next_token.position)
                return left

            # Create binary expression node, and assign it as the left operand for the next iteration.
            position = left.position
            left = BinaryExpressionNode(operator.kind, left, right)
            left.position = position
            operator = self.lexer.peek()

        return left

    def __parse_type(self) -> TypeNode | None:
        token = self.lexer.peek()

        if token.kind == '(':
            return self.__parse_function_type()
        elif token.kind == 'Nil':
            node = NilTypeNode()
        elif token.kind == 'Bool':
            node = BoolTypeNode()
        elif token.kind == 'Real':
            node = RealTypeNode()
        elif token.kind == 'String':
            node = StringTypeNode()
        else:
            return None

        node.position = token.position
        self.lexer.scan()
        return node

    def __parse_function_type(self) -> FunctionTypeNode | None:

        position = self.lexer.peek().position
        self.__expect('(', 'to open function type')
        parameter_types = self.__parse_type_list()
        self.__expect(')', 'to close function type')
        self.__expect('->', 'to specify return type')
        return_type = self.__expect_type('after ->') or AnyTypeNode()
        node = FunctionTypeNode(parameter_types, return_type)
        node.position = position
        return node

    def __parse_type_list(self):
        types: List[TypeNode] = []
        while True:
            type = self.__parse_type()
            if type is None:
                break
            types.append(type)
            if self.lexer.peek().kind != ',':
                break
            self.lexer.scan()
        return types

    def __parse_expression_list(self):
        expressions: List[ExpressionNode] = []
        token = self.lexer.peek()

        while token.kind != ')' and token.kind != 'eof':
            expression = self.__expect_expression('to specify argument')
            if expression is None:
                token = self.lexer.scan()  # skip token
                continue

            expressions.append(expression)
            token = self.lexer.peek()

            if token.kind == ',':
                self.lexer.scan()
            elif token.kind != ')':
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected , or ) after expression (got {token})', token.position)

            token = self.lexer.peek()

        return expressions

    def __expect(self, kind: str, reason: str) -> Optional[str]:
        token = self.lexer.peek()
        if token.kind == kind:
            self.lexer.scan()
            return token.lexeme
        else:
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected {kind} (got {token}) {reason}', token.position)
            return None

    def __expect_type(self, context: str) -> Optional[TypeNode]:
        type_token = self.lexer.peek()
        type = self.__parse_type()
        if type is None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected type (got {type_token}) {context}', type_token.position)
        return type

    def __expect_statement(self, context: str) -> Optional[StatementNode]:
        stmt_token = self.lexer.peek()
        stmt = self.__parse_statement()
        if stmt is None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected statement (got {stmt_token}) {context}', stmt_token.position)
        return stmt

    def __expect_expression(self, context: str) -> Optional[ExpressionNode]:
        expr_token = self.lexer.peek()
        expr = self.__parse_expression()
        if expr is None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected expression (got {expr_token}) {context}', expr_token.position)
        return expr
