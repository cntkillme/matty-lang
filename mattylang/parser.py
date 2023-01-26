from mattylang.lexer import Lexer
from mattylang.nodes import *


class Parser:
    def __init__(self, lexer: Lexer):
        self.__module = lexer.get_module()
        self.__lexer = lexer
        self.__program: Optional[ProgramNode] = None

    def get_module(self):
        return self.__module

    def parse(self) -> ProgramNode:
        if self.__program is None:
            self.__program = self.__parse_program()
            self.__expect('eof', 'to end program')
        return self.__program

    def __expect(self, kind: str, reason: str) -> str | None:
        token = self.__lexer.peek()
        if token.kind == kind:
            self.__lexer.scan()
            return token.lexeme
        else:
            self.__module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected {kind} (got {token}) {reason}', token.position)
            return None

    def __expect_statement(self, context: str) -> Optional[StatementNode]:
        stmt_token = self.__lexer.peek()
        stmt = self.__parse_statement()
        if stmt is None:
            self.__module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected statement (got {stmt_token}) {context}', stmt_token.position)
        else:
            stmt.position = stmt_token.position
        return stmt

    def __expect_statement_or(self, context: str, default: StatementNode) -> StatementNode:
        stmt_token = self.__lexer.peek()
        stmt = self.__expect_statement(context)
        if stmt is None:
            stmt = default
            stmt.position = stmt_token.position
            stmt.invalid = True
        return stmt

    def __expect_expression(self, context: str) -> Optional[ExpressionNode]:
        expr_token = self.__lexer.peek()
        expr = self.__parse_expression()
        if expr is None:
            self.__module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected expression (got {expr_token}) {context}', expr_token.position)
        else:
            expr.position = expr_token.position
        return expr

    def __expect_expression_or(self, context: str, default: ExpressionNode) -> ExpressionNode:
        expr_token = self.__lexer.peek()
        expr = self.__expect_expression(context)
        if expr is None:
            expr = default
            expr.position = expr_token.position
            expr.invalid = True
        return expr

    def __parse_program(self) -> ProgramNode:
        program = ProgramNode(self.__parse_chunk(terminate='eof'))
        return program

    def __parse_chunk(self, terminate: str) -> ChunkNode:
        chunk = ChunkNode()
        token = self.__lexer.peek()
        while token.kind != 'eof' and token.kind != terminate:
            position = token.position
            statement = self.__parse_statement()
            if statement is not None:
                statement.position = position
                statement.parent = chunk
                chunk.statements.append(statement)
            token = self.__lexer.peek()
        return chunk

    def __parse_statement(self) -> StatementNode | None:
        token = self.__lexer.peek()
        if token.kind == '{':  # block
            self.__lexer.scan()
            chunk = self.__parse_chunk(terminate='}')
            self.__expect('}', 'to close block')
            return chunk
        elif token.kind == 'def':  # variable definition
            return self.__parse_variable_definition()
        elif token.kind == 'if':  # if statement
            return self.__parse_if_statement()
        elif token.kind == 'while':  # while statement
            return self.__parse_while_statement()
        elif token.kind == 'break':  # break statement
            self.__lexer.scan()
            return BreakStatementNode()
        elif token.kind == 'continue':  # continue statement
            self.__lexer.scan()
            return ContinueStatementNode()
        elif token.kind == 'identifier':  # variable assignment
            identifier = IdentifierNode(token.lexeme)
            identifier.position = token.position
            self.__lexer.scan()  # skip identifier

            if self.__lexer.peek().kind == '=':
                return self.__parse_variable_assignment(identifier)
            else:
                self.__module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {identifier}', identifier.position)
                return None

        else:
            # Greedy recovery: try to parse an expression if no statement can be parsed.
            # This is done to minimize the number of diagnostics produced.
            position = token.position
            expression = self.__parse_expression()

            if expression is not None:
                expression.position = position
                self.__module.diagnostics.emit_diagnostic(
                    'error', f'syntax: unexpected {expression}', position)
                return None

            self.__module.diagnostics.emit_diagnostic(
                'error', f'syntax: expected statement (got {token})', position)
            self.__lexer.scan()  # warning: parse_statement will advance the lexer even if no statement was parsed
            return None

    __binary_operators = {
        '&&': 1, '||': 1,
        '<': 2, '>': 2, '<=': 2, '>=': 2, '==': 2, '!=': 2,
        '+': 3, '-': 3,
        '*': 4, '/': 4, '%': 4,
    }

    def __parse_variable_definition(self) -> VariableDefinitionNode | None:
        """
        variable_definition = "def" identifier "=" expression;

        Recovery: if no identifier, emit error and skip to next statement.
        Recovery: if missing "=", or missing expression, emit error and set initializer to NilLiteralNode.
        """
        self.__lexer.scan()  # skip 'def'
        name_token = self.__lexer.peek()
        name = self.__expect('identifier', 'to name variable')

        if name is None:
            return None

        if self.__expect('=', f'to initialize variable {name}') is None:
            initializer = NilLiteralNode()
            initializer.position = self.__lexer.peek().position
            initializer.invalid = True
        else:
            # MattyLang v2.0 idea: allow explicit typing of variables with a sane default if no initializer is provided.
            initializer = self.__expect_expression_or(f'to initialize variable {name}', NilLiteralNode())

        identifier = IdentifierNode(name)
        identifier.position = name_token.position
        return VariableDefinitionNode(identifier, initializer)

    def __parse_variable_assignment(self, identifier: IdentifierNode) -> VariableAssignmentNode | None:
        """
        variable_assignment = identifier "=" expression;

        Recovery: if missing "=", or missing expression, emit error and skip.
        """
        self.__lexer.scan()  # skip '='
        initializer = self.__expect_expression(f'to assign variable {identifier.value}')
        if initializer is None:
            return None
        return VariableAssignmentNode(identifier, initializer)

    def __parse_if_statement(self) -> IfStatementNode | None:
        """
        if_statement = "if" "(" expression ")" statement [ "else" statement ];

        Recovery: if missing "(" or ")", emit error and continue.
        Recovery: if missing condition, emit error and set condition to BoolLiteralNode(False).
        Recovery: if missing statement, emit error and set body to ChunkNode().
        Recovery: if has "else" but missing statement, emit error and continue.
        """
        self.__lexer.scan()  # skip 'if'
        self.__expect('(', 'to open if condition')
        if_condition = self.__expect_expression_or('after if', BoolLiteralNode(False))
        self.__expect(')', 'to close if condition')
        if_body = self.__expect_statement_or('after if', ChunkNode())
        else_body = None
        has_else_with_no_body = False

        if self.__lexer.peek().kind == 'else':
            self.__lexer.scan()  # skip 'else'
            else_body = self.__expect_statement('after else')
            if else_body is None:
                has_else_with_no_body = True

        node = IfStatementNode(if_condition, if_body, else_body)
        node.invalid = node.invalid or has_else_with_no_body
        return node

    def __parse_while_statement(self) -> WhileStatementNode | None:
        """
        while_statement = "while" "(" expression ")" statement;

        Recovery: if missing "(" or ")", emit error and continue.
        Recovery: if missing condition, emit error and set condition to BoolLiteralNode(False).
        Recovery: if missing statement, emit error and set body to ChunkNode().
        """
        self.__lexer.scan()  # skip 'while'
        self.__expect('(', 'to open while condition')
        condition = self.__expect_expression_or('after while', BoolLiteralNode(False))
        self.__expect(')', 'to close while condition')
        body = self.__expect_statement_or('after while', ChunkNode())
        return WhileStatementNode(condition, body)

    def __parse_expression(self) -> ExpressionNode | None:
        return self.__parse_binary_expression(0)

    def __parse_binary_expression(self, precedence: int) -> ExpressionNode | None:
        left = self.__parse_unary_expression()
        operator = self.__lexer.peek()

        # Keep parsing expressions at or greater precedence of the current operator.
        # Example: `1 + 2 - 3` will be parsed as `(1 + 2) - 3`
        while left is not None and self.__binary_operators.get(operator.kind, -1) >= precedence:
            token = self.__lexer.peek()
            next_token = self.__lexer.scan()  # skip operator

            # Parse sub-expressions of right operand with higher precedence than the current operator.
            # Example: `1 + 2 * 3` will be parsed as `1 + (2 * 3)`
            right = self.__parse_binary_expression(self.__binary_operators[operator.kind] + 1)

            if not right:
                self.__module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression (got {next_token}) after {token}', next_token.position)
                return left

            # Create binary expression node, and assign it as the left operand for the next iteration.
            position = left.position
            left = BinaryExpressionNode(operator.kind, left, right)
            left.position = position
            operator = self.__lexer.peek()

        return left

    __unary_operators = {
        '!': True,
        '-': True
    }

    def __parse_unary_expression(self) -> ExpressionNode | None:
        operator = self.__lexer.peek()

        if operator.kind in self.__unary_operators:
            self.__lexer.scan()  # skip operator
            operand = self.__parse_unary_expression()
            next_token = self.__lexer.peek()

            if operand is None:
                self.__module.diagnostics.emit_diagnostic(
                    'error', f'syntax: expected expression after {operator} (got {next_token})', next_token.position)
                return None

            expr = UnaryExpressionNode(operator.kind, operand)
            expr.position = operator.position
            return expr
        else:
            return self.__parse_primary_expression()

    def __parse_primary_expression(self) -> ExpressionNode | None:
        token = self.__lexer.peek()

        if token.kind == '(':
            self.__lexer.scan()
            expression = self.__parse_expression()
            self.__expect(')', 'to close expression')
            return expression
        elif token.kind == 'nil':
            self.__lexer.scan()
            node = NilLiteralNode()
        elif token.kind == 'true':
            self.__lexer.scan()
            node = BoolLiteralNode(True)
        elif token.kind == 'false':
            self.__lexer.scan()
            node = BoolLiteralNode(False)
        elif token.kind == 'real_literal':
            # precondition: token.lexeme is a valid float literal (lexer invariant)
            self.__lexer.scan()
            node = RealLiteralNode(float(token.lexeme))
        elif token.kind == 'string_literal':
            self.__lexer.scan()
            node = StringLiteralNode(token.lexeme)
        elif token.kind == 'identifier':
            self.__lexer.scan()
            node = IdentifierNode(token.lexeme)
        else:
            return None

        node.position = token.position
        return node
