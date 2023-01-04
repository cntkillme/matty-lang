import unittest

from mattylang.module import Module
from mattylang.lexer import Lexer, Token


class TestV1(unittest.TestCase):
    def test_tokens(self):
        source = '''
        # keywords
        def nil true false
        # punctuation
        ( ) { } = ! + - * / % < > == != <= >= || &&
        # identifiers
        a a1 $a _a $1 _1
        # literals
        1 5. .5 5.5 \'hello\' "hello"

        # lexer diagnostics
        . 1a ` "asd
        '''
        source_tokens = [
            'def', 'nil', 'true', 'false',
            '(', ')', '{', '}', '=', '!', '+', '-', '*', '/', '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&',
            'identifier(a)', 'identifier(a1)', 'identifier($a)', 'identifier(_a)', 'identifier($1)', 'identifier(_1)',
            'real_literal(1)', 'real_literal(5.)', 'real_literal(.5)', 'real_literal(5.5)', "string_literal('hello')", "string_literal('hello')",
        ]
        source_diagnostics = ['error', 'warning', 'error', 'error']
        module = Module('test.mty', source)
        tokens = list(map(str, self.__get_tokens(module)))
        self.assertEqual(tokens, source_tokens)
        self.assertEqual([diagnostic.kind for diagnostic in module.diagnostics], source_diagnostics)

    def test_compiler(self):
        # TODO
        _ = '''
        { # chunk
            # arithmetic operators
            def x = -(0 + 1)*2 - (8/2)%2 # -2
            # relational operators
            def y = 1 < 2 && 2 > 1 && 1 <= 2 && 2 >= 1 && 1 == 1 && 1 != 2
            # logical operators
            def b = y || (!!true && !false)
            b = true
        }
        '''

    def __get_tokens(self, module: Module):
        lexer = Lexer(module)
        tokens: list[Token] = []
        while lexer.token.kind != 'eof':
            tokens.append(lexer.token)
            lexer.scan()
        return tokens


if __name__ == '__main__':
    unittest.main()
