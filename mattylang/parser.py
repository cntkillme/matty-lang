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
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected {kind} (got {token}) {reason}', token.position)
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
                statement.parent = chunk
                chunk.statements.append(statement)
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
                return None  # recovery: skip entire statement

            # diagnostic: expected expression to initialize variable
            if self.__expect('=', f'to initialize variable {name}') is None:
                initializer = NilLiteralNode()
                initializer.position = self.lexer.token.position
                initializer.invalid = True
            else:
                token = self.lexer.token
                initializer = self.__parse_expression()

                # diagnostic: expected expression to initialize variable
                if initializer is None:
                    initializer = NilLiteralNode()
                    initializer.position = token.position
                    initializer.invalid = True
                    self.module.diagnostics.emit_diagnostic(
                        'error', f'syntax: expected expression (got {token}) to initialize variable {name}', token.position)

            identifier = IdentifierNode(name)
            identifier.position = name_token.position
            initializer = initializer or NilLiteralNode()
            node = VariableDefinitionNode(identifier, initializer)
            node.position = def_token.position
            node.invalid = identifier.invalid or initializer.invalid
            return node
        elif token.kind == 'identifier':  # variable assignment
            name = token.lexeme
            self.lexer.scan()

            # diagnostic: unexpected expression
            if self.lexer.token.kind != '=':
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected identifier {name}', token.position)
                return None  # recovery: skip expression

            self.lexer.scan()
            identifier = IdentifierNode(name)
            identifier.position = token.position
            initializer = self.__parse_expression()

            # diagnostic: expected expression to assign variable
            if initializer is None:
                token = self.lexer.token
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression (got {token}) to assign to variable {name}', token.position)
                return None  # recovery: skip statement

            node = VariableAssignmentNode(identifier, initializer)
            node.position = token.position
            return node
        else:
            expression = self.__parse_expression()

            # diagnostic: unexpected expression
            if expression is not None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {expression}', expression.position)
                return None  # recovery: skip expression

            # diagnostic: expected statement
            self.module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected statement (got {token})', token.position)
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
        operator = self.lexer.token

        # Keep parsing expressions at or greater precedence of the current operator.
        # Example: `1 + 2 - 3` will be parsed as `(1 + 2) - 3`
        while left is not None and self.__binary_operators.get(operator.kind, -1) >= precedence:
            token = self.lexer.token
            next_token = self.lexer.scan()  # skip operator

            # Parse sub-expressions of right operand with higher precedence than the current operator.
            # Example: `1 + 2 * 3` will be parsed as `1 + (2 * 3)`
            right = self.__parse_binary_expression(self.__binary_operators[operator.kind] + 1)

            # diagnostic: expected expression after binary operator
            if not right:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression after {token} (got {next_token})', next_token.position)
                return left  # recovery: yield the left operand

            # Create binary expression node, and assign it as the left operand for the next iteration.
            position = left.position
            left = BinaryExpressionNode(operator.kind, left, right)
            left.position = position
            operator = self.lexer.token

        return left

    __unary_operators = {
        '!': True,
        '-': True
    }

    def __parse_unary_expression(self) -> ExpressionNode | None:
        operator = self.lexer.token

        if operator.kind in self.__unary_operators:
            self.lexer.scan()  # skip operator
            operand = self.__parse_unary_expression()
            next_token = self.lexer.token

            # diagnostic: expected expression after unary operator
            if operand is None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression after {operator} (got {next_token})', next_token.position)
                return None  # recovery: skip entire expression

            expr = UnaryExpressionNode(operator.kind, operand)
            expr.position = operator.position
            return expr
        else:
            return self.__parse_primary_expression()

    def __parse_primary_expression(self) -> ExpressionNode | None:
        token = self.lexer.token

        if token.kind == '(':
            self.lexer.scan()
            expression = self.__parse_expression()
            # diagnostic: expected ')'
            self.__expect(')', 'to close expression')
            return expression   # recovery: implicitly close unclosed expressions.
        elif token.kind == 'nil':
            self.lexer.scan()
            node = NilLiteralNode()
        elif token.kind == 'true':
            self.lexer.scan()
            node = BoolLiteralNode(True)
        elif token.kind == 'false':
            self.lexer.scan()
            node = BoolLiteralNode(False)
        elif token.kind == 'real_literal':
            # precondition: token.lexeme is a valid float literal (lexer invariant)
            self.lexer.scan()
            node = RealLiteralNode(float(token.lexeme))
        elif token.kind == 'string_literal':
            self.lexer.scan()
            node = StringLiteralNode(token.lexeme)
        elif token.kind == 'identifier':
            self.lexer.scan()
            node = IdentifierNode(token.lexeme)
        else:
            return None

        node.position = token.position
        return node
