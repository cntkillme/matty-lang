from mattylang.lexer import Lexer
from mattylang.nodes import *


class Parser:
    def __init__(self, lexer: Lexer):
        self.module = lexer.module
        self.lexer = lexer
        self.program = self.__parse()

    def __parse(self):
        program = self.__parse_program()
        self.__expect('eof', 'to end program')
        return program

    def __expect(self, kind: str, reason: str) -> str | None:
        token = self.lexer.token
        if token.kind == kind:
            self.lexer.scan()
            return token.lexeme
        else:
            # diagnostic: expected token
            self.module.diagnostics.emit_error(
                f'expected {kind} (got {token}) {reason}', token.line, token.column)
            return None

    def __parse_program(self) -> ProgramNode:
        program = ProgramNode(self.__parse_chunk(terminate='eof'))
        return program

    def __parse_chunk(self, terminate: str) -> ChunkNode:
        chunk = ChunkNode()
        kind = self.lexer.token.kind
        while kind != 'eof' and kind != terminate:
            statement = self.__parse_statement()
            if statement is not None:
                chunk.add_statement(statement)
            kind = self.lexer.token.kind
        return chunk

    def __parse_statement(self) -> StatementNode | None:
        token = self.lexer.token
        if token.kind == '{':  # block
            self.lexer.scan()
            chunk = self.__parse_chunk(terminate='}')
            self.__expect('}', 'to close block')
            return chunk
        elif token.kind == 'def':  # variable definition
            def_token = token
            self.lexer.scan()
            name_token = self.lexer.token
            name = self.__expect('identifier', 'to name variable')

            # diagnostic: expected identifier to name variable
            if name is None:
                self.module.diagnostics.emit_error(
                    f'expected identifier (got {token}) to name variable', token.line, token.column)
                return None  # recovery: skip entire statement

            # diagnostic: expected expression to initialize variable
            if self.__expect('=', f'to initialize variable {name}') is None:
                initializer = NilLiteralNode().add_token(self.lexer.token)
                initializer.invalid = True
            else:
                initializer_token = self.lexer.token
                initializer = self.__parse_expression()

                # diagnostic: expected expression to initialize variable
                if initializer is None:
                    initializer = NilLiteralNode().add_token(initializer_token)
                    initializer.invalid = True
                    self.module.diagnostics.emit_error(
                        f'expected expression (got {initializer_token}) to initialize variable {name}', initializer_token.line, initializer_token.column)

            identifier = IdentifierNode(name).add_token(name_token)
            initializer = initializer or NilLiteralNode().add_token(self.lexer.token)
            node = VariableDefinitionNode(identifier, initializer).add_token(def_token)
            node.invalid = identifier.invalid or initializer.invalid
            return node
        elif token.kind == 'identifier':  # variable assignment
            first_token = token
            name = token.lexeme
            self.lexer.scan()

            # diagnostic: expected = to assign variable
            if self.__expect('=', f'to assign variable {name}') is None:
                return None

            identifier = IdentifierNode(name).add_token(first_token)
            initializer = self.__parse_expression()

            # diagnostic: expected expression to assign variable
            if initializer is None:
                token = self.lexer.token
                self.module.diagnostics.emit_error(
                    f'expected expression (got {token}) to assign to variable {name}', token.line, token.column)
                return None  # recovery: skip statement

            return VariableAssignmentNode(identifier, initializer).add_token(first_token)
        else:
            expression = self.__parse_expression()

            # diagnostic: unused expression
            if expression is not None:
                self.module.diagnostics.emit_error(f'unused expression {expression}', *expression.get_location())
                return None  # recovery: skip expression

            # diagnostic: statement expected
            self.module.diagnostics.emit_error(
                f'expected statement (got {token})', token.line, token.column)
            self.lexer.scan()  # warning: parse_statement will advance the lexer even if no statement was parsed
            return None  # recovery: skip token

    __binary_operators = {
        '&&': 1, '||': 1,
        '<': 2, '>': 2, '<=': 2, '>=': 2, '==': 2, '!=': 2,
        '+': 3, '-': 3,
        '*': 4, '/': 4, '%': 4,
    }

    def __parse_expression(self) -> ExpressionNode | None:
        return self.__parse_binary_expression(0)

    def __parse_binary_expression(self, precedence: int) -> ExpressionNode | None:
        left = self.__parse_unary_expression()
        operator = self.lexer.token.kind

        # Keep parsing expressions at or greater precedence of the current operator.
        # Example: `1 + 2 - 3` will be parsed as `(1 + 2) - 3`
        while left is not None and self.__binary_operators.get(operator, -1) >= precedence:
            token = self.lexer.token
            next_token = self.lexer.scan()  # skip operator

            # Parse sub-expressions of right operand with higher precedence than the current operator.
            # Example: `1 + 2 * 3` will be parsed as `1 + (2 * 3)`
            right = self.__parse_binary_expression(self.__binary_operators[operator] + 1)

            # diagnostic: expected expression after binary operator
            if not right:
                self.module.diagnostics.emit_error(
                    f'expected expression after {token} (got {next_token})', next_token.line, next_token.column)
                return left  # recovery: yield the left operand

            # Create binary expression node, and assign it as the left operand for the next iteration.
            left = BinaryExpressionNode(operator, left, right)
            if left.left.token is not None:
                left.add_token(left.left.token)
            operator = self.lexer.token.kind

        return left

    __unary_operators = {
        '!': True,
        '-': True
    }

    def __parse_unary_expression(self) -> ExpressionNode | None:
        token = self.lexer.token

        if token.kind in self.__unary_operators:
            self.lexer.scan()  # skip operator
            operand = self.__parse_unary_expression()
            next_token = self.lexer.token

            # diagnostic: expected expression after unary operator
            if operand is None:
                self.module.diagnostics.emit_error(
                    f'expected expression after {token} (got {next_token})', next_token.line, next_token.column)
                return None  # recovery: skip entire expression

            expr = UnaryExpressionNode(token.kind, operand).add_token(token)
            return expr
        else:
            return self.__parse_primary_expression()

    def __parse_primary_expression(self) -> ExpressionNode | None:
        token = self.lexer.token

        if token.kind == '(':
            self.lexer.scan()
            expression = self.__parse_expression()
            self.__expect(')', 'to close expression')
            return expression   # recovery: implicitly close unclosed expressions.
        elif token.kind == 'nil':
            self.lexer.scan()
            return NilLiteralNode().add_token(token)
        elif token.kind == 'true':
            self.lexer.scan()
            return BoolLiteralNode(True).add_token(token)
        elif token.kind == 'false':
            self.lexer.scan()
            return BoolLiteralNode(False).add_token(token)
        elif token.kind == 'real_literal':
            # precondition: token.lexeme is a valid float literal (lexer invariant)
            value = float(token.lexeme)
            self.lexer.scan()
            return RealLiteralNode(value).add_token(token)
        elif token.kind == 'string_literal':
            value = token.lexeme
            self.lexer.scan()
            return StringLiteralNode(value).add_token(token)
        elif token.kind == 'identifier':
            self.lexer.scan()
            return IdentifierNode(token.lexeme).add_token(token)
        else:
            return None
