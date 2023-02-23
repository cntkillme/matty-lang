import unittest

from mattylang.ast import IdentifierNode
from mattylang.symbols import SymbolTable


class TestSymbols(unittest.TestCase):
    def test_symbols(self):
        scope = SymbolTable()

        self.assertEqual(scope.lookup('a'), None)
        symbol = scope.register('a')
        self.assertEqual(scope.lookup('a', False), symbol)  # non-recursive lookup
        self.assertEqual(scope.lookup('a'), symbol)  # recursive lookup
        self.assertEqual(scope.enclosing_boundary(), None)

        subscope = scope.open_scope(boundary=True)
        self.assertEqual(subscope.lookup('a'), None)  # stops lookup at boundary
        self.assertEqual(subscope.lookup('a', ignore_boundary=True), symbol)  # ignores boundary
        self.assertEqual(subscope.lookup('a', False, ignore_boundary=True), None)  # ignores boundary, not-recursive
        symbol2 = subscope.register('a')

        subscope2 = subscope.open_scope()
        self.assertEqual(subscope2.lookup('a', False), None)  # non-recursive lookup
        self.assertEqual(subscope2.lookup('a'), symbol2)  # recursive lookup
        self.assertEqual(subscope2.enclosing_boundary(), subscope)

        subscope3 = subscope2.open_scope()
        self.assertEqual(subscope3.enclosing_boundary(), subscope)
        self.assertEqual(subscope3.close_scope(), subscope2)

        id = IdentifierNode(0, 'a')
        symbol.references.append(id)
        self.assertEqual(id.value, 'a')
        symbol.rename('b')
        self.assertEqual(id.value, 'b')
        self.assertEqual(scope.lookup('a'), None)
        self.assertEqual(scope.lookup('b'), symbol)
        self.assertEqual(subscope.lookup('a'), symbol2)
        self.assertEqual(subscope.lookup('b', False), None)
        symbol.erase()
        self.assertEqual(scope.lookup('b'), None)
        self.assertRegex(str(symbol), 'name: b')
