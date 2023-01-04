from typing import TYPE_CHECKING, Dict, List, Optional

from mattylang.ast.core import Declaration

if TYPE_CHECKING:
    from mattylang.ast.expression import IdentifierNode
    from mattylang.ast.type import TypeNode


class Symbol:
    def __init__(self, scope: 'SymbolTable', declaration: 'Declaration'):
        self.scope = scope
        self.declaration = declaration
        self.references: List['IdentifierNode'] = []
        self.type: Optional['TypeNode'] = None

    def __str__(self):
        return f'symbol({self.declaration.get_declared_name()})'


class SymbolTable:
    """
    A data structure used to store symbols and their declarations.
    """

    def __init__(self, parent: Optional['SymbolTable'] = None, boundary: bool = False):
        self.parent = parent  # represents the scope this scope is nested within
        self.children: List[SymbolTable] = []  # represents the scopes nested within this scope
        self.symbols: Dict[str, Symbol] = {}  # represents the symbols declared in this scope
        self.boundary = boundary  # represents whether this scope is a boundary (e.g., at function definitions)

    def __str__(self):
        return f'symbol_table({len(self.symbols)}, boundary={self.boundary})'

    def enclosing_boundary(self) -> Optional['SymbolTable']:
        if self.parent is None:
            return None
        elif self.parent.boundary:
            return self.parent
        else:
            return self.parent.enclosing_boundary()

    def lookup(self, name: str, recursive: bool = True, ignore_boundary: bool = False) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        elif recursive and self.parent is not None and (ignore_boundary or not self.boundary):
            return self.parent.lookup(name, True, ignore_boundary)
        else:
            return None

    def register(self, declaration: 'Declaration'):
        name = declaration.get_declared_name()
        # fatal: duplicate declaration
        assert name not in self.symbols, f'fatal: symbol {name} already defined in SymbolTable {self}'
        symbol = Symbol(self, declaration)
        self.symbols[name] = symbol
        return symbol

    def open_scope(self):
        scope = SymbolTable()
        scope.parent = self
        self.children.append(scope)
        return scope

    def close_scope(self):
        parent = self.parent
        assert parent is not None, 'fatal: scope underflow'
        return parent

    def destroy_scope(self):
        parent = self.parent
        assert parent is not None, 'fatal: scope underflow'
        parent.children.remove(self)
        self.parent = None
        return parent
