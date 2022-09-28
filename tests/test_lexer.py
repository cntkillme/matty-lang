import unittest

from mattylang.module import Module
from mattylang.lexer import Lexer
from mattylang.iterator import TokenIterator


class TestLexer(unittest.TestCase):
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
        '''
        source_tokens = [
            'def', 'nil', 'true', 'false',
            '(', ')', '{', '}', '=', '!', '+', '-', '*', '/', '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&',
            'identifier(a)', 'identifier(a1)', 'identifier($a)', 'identifier(_a)', 'identifier($1)', 'identifier(_1)',
            'int_literal(1)', 'real_literal(5.)', 'real_literal(.5)', 'real_literal(5.5)', "string_literal('hello')", "string_literal('hello')",
        ]
        source_diagnostics = []
        module = Module('test.mty', source)
        lexer = Lexer(module)
        tokens = [str(token) for token in TokenIterator(lexer)]
        self.assertEqual(tokens, source_tokens)
        self.assertEqual([diagnostic.kind for diagnostic in module.get_diagnostics()], source_diagnostics)

    def test_diagnostics(self):
        source = '''
        . 1a
        "asd
        `
        '''
        source_tokens = ['real_literal(0.0)', 'int_literal(1)', 'identifier(a)', "string_literal('asd')"]
        source_diagnostics = ['error', 'warning', 'error', 'error']
        module = Module('test.mty', source)
        lexer = Lexer(module)
        tokens = [str(token) for token in TokenIterator(lexer)]
        self.assertEqual(tokens, source_tokens)
        self.assertEqual([diagnostic.kind for diagnostic in module.get_diagnostics()], source_diagnostics)


if __name__ == '__main__':
    unittest.main()
