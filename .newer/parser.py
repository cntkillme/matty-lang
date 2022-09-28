from typing import List
from compiler.lexer import Lexer
from compiler.nodes import *


class Parser:
    def __init__(self, lexer: Lexer):
        self.__lexer = lexer
        self.__program = self.__parse()

    def get_program(self):
        return self.__program

    def __parse(self):
        program = self.__parse_program()
        self.__expect('eof')
        return program

    def __expect(self, kind: str):
        token = self.__lexer.token
        if token[0] == kind:
            self.__lexer.scan()
            return token[1]
        else:
            raise ValueError('expected token', kind, 'got', token[0])

    def __parse_program(self) -> ProgramNode:
        return ProgramNode(self.__parse_chunk(terminate='eof'))

    def __parse_chunk(self, terminate: str) -> ChunkNode:
        statements: List[StatementNode] = []
        while self.__lexer.token[0] != 'eof' and self.__lexer.token[0] != terminate:
            statements.append(self.__parse_statement())
        return ChunkNode(statements)

    def __parse_statement(self) -> StatementNode:
        token = self.__lexer.token
        if token[0] == '{':  # block
            self.__lexer.scan()
            chunk = self.__parse_chunk(terminate='}')
            self.__expect('}')
            return chunk
        elif token[0] == 'def':  # variable definition
            self.__lexer.scan()
            name = self.__parse_identifier()
            self.__expect('=')
            return VariableDefinitionNode(name, self.__parse_expression())
        elif token[0] == '<identifier>':  # variable assignment
            name = self.__parse_identifier()
            self.__expect('=')
            return VariableAssignmentNode(name, self.__parse_expression())
        else:
            raise ValueError('unexpected token', self.__lexer.token[0])

    # increasing precedence
    __binary_operators = {
        '&&': 1, '||': 1,
        '<': 2, '>': 2, '<=': 2, '>=': 2, '==': 2, '!=': 2,
        '+': 3, '-': 3,
        '*': 4, '/': 4, '%': 4,
    }

    def __parse_expression(self) -> ExpressionNode:
        return self.__parse_binary_expression(0)

    def __parse_binary_expression(self, precedence: int) -> ExpressionNode:
        left = self.__parse_unary_expression()
        token = self.__lexer.token[0]
        while token in self.__binary_operators and self.__binary_operators[token] >= precedence:
            operator = token
            self.__lexer.scan()
            right = self.__parse_binary_expression(
                self.__binary_operators[operator] + 1)
            left = BinaryExpressionNode(operator, left, right)
            token = self.__lexer.token[0]
        return left

    __unary_operators = {
        '!': True,
        '-': True
    }

    def __parse_unary_expression(self) -> ExpressionNode:
        token = self.__lexer.token
        if token[0] in self.__unary_operators:
            self.__lexer.scan()
            return UnaryExpressionNode(token[0], self.__parse_unary_expression())
        else:
            return self.__parse_primary_expression()

    def __parse_primary_expression(self) -> ExpressionNode:
        token = self.__lexer.token
        if token[0] == '(':
            self.__lexer.scan()
            expression = self.__parse_expression()
            self.__expect(')')
            return expression
        elif token[0] == 'nil':
            self.__lexer.scan()
            return NilLiteralNode()
        elif token[0] == 'true':
            self.__lexer.scan()
            return BoolLiteralNode(True)
        elif token[0] == 'false':
            self.__lexer.scan()
            return BoolLiteralNode(False)
        elif token[0] == '<real>':
            value = float(token[1])
            self.__lexer.scan()
            return RealLiteralNode(value)
        elif token[0] == '<string>':
            value = token[1]
            self.__lexer.scan()
            return StringLiteralNode(value)
        elif token[0] == '<identifier>':
            return self.__parse_identifier()
        else:
            raise ValueError('unexpected token', token)

    def __parse_identifier(self) -> IdentifierNode:
        return IdentifierNode(self.__expect('<identifier>'))
