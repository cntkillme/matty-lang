import unittest
from typing import List, Tuple

from mattylang.lexer import Lexer, Token
from mattylang.module import Module


class TokensTest(unittest.TestCase):
    def test_token(self):
        expected = ['def', 'identifier(x)', 'real_literal(1.0)', "string_literal('1.0')"]
        lexer = Lexer(Module('test', 'def x 1.0 "1.0"'))

        # get tokens
        tokens: List[Token] = []
        while lexer.peek().kind != 'eof':
            tokens.append(lexer.peek())
            lexer.scan()

        result = list(map(str, tokens))
        self.assertEqual(expected, result)

    def test_lexer(self):
        expected = [
            'def', 'nil', 'true', 'false', 'if', 'else', 'while',
            'break', 'continue', 'return', 'Nil', 'Bool', 'Real', 'String',
            '(', ')', '{', '}', '=', '!', '+', '-', '*', '/',
            '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&', ':', '->', ',',
            ('identifier', 'x'),
            ('real_literal', '1'),
            ('real_literal', '1.0'),
            ('string_literal', 'hello, world'),
            ('string_literal', "'hello, world'"),
        ]

        def to_lexeme(token: str | Tuple[str, str]):
            if isinstance(token, str):
                return token
            else:
                kind, lexeme = token
                if kind == 'string_literal':
                    return repr(lexeme)
                else:
                    return lexeme

        def from_token(token: Token) -> str | Tuple[str, str]:
            if token.kind == 'identifier':
                return 'identifier', token.lexeme
            elif token.kind == 'real_literal':
                return 'real_literal', token.lexeme
            elif token.kind == 'string_literal':
                return 'string_literal', token.lexeme
            else:
                return token.kind

        source = (' ').join(map(to_lexeme, expected))
        lexer = Lexer(Module('test', source))

        # get tokens
        tokens: List[Token] = []
        while lexer.peek().kind != 'eof':
            tokens.append(lexer.peek())
            lexer.scan()

        result = list(map(from_token, tokens))

        # compare result and expected
        self.assertEqual(result, expected)

    def test_diagnostics(self):
        expected = [
            ('error', 'expected digits around decimal point'),
            ('warning', 'expected whitespace after real literal'),
            ('error', 'terminate string'),
            ('error', 'unexpected character')
        ]

        source = ' .\n1.a\n# asd\n"asd\n;'
        lexer = Lexer(Module('test', source))
        print("PEEK", lexer.peek())
        self.assertEqual(lexer.token_position(), 1)

        # get tokens
        tokens: List[Token] = []
        while lexer.peek().kind != 'eof':
            tokens.append(lexer.peek())
            lexer.scan()

        # compare diagnostics
        result = [(diagnostic.kind, expected[idx][1] if diagnostic.message.find(expected[idx][1]) != -
                   1 else diagnostic.message) for idx, diagnostic in enumerate(lexer.module.diagnostics)]
        self.assertEqual(result, expected)