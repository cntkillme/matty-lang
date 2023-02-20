from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mattylang.ast import *


class Symbol:
    """
    A symbol represents a registered variable declaration in the program.
    """

    def __init__(self, name: str, scope: 'SymbolTable', extern: bool = False, node: Optional['AbstractNode'] = None, type: Optional['TypeNode'] = None):
        self.name = name
        self.scope = scope
        self.extern = extern
        self.references: List[IdentifierNode] = []  # set by binder
        self.node = node  # set by binder
        self.type = type  # set by checker

    def __str__(self):
        return f'symbol(name: {self.name}, node: {self.node}, type: {self.type}, extern: {self.extern})'

    def get_node(self) -> 'AbstractNode':
        assert self.node is not None, 'node is not set for {self}, was the binder run?'
        return self.node

    def get_type(self) -> 'TypeNode':
        assert self.type is not None, 'type is not set for {self}, was the checker run?'
        return self.type

    def rename(self, new_name: str):
        scope = self.scope
        assert new_name not in scope.variables, f'fatal: symbol {new_name} already defined'

        # rename symbol
        scope.variables[new_name] = self
        del scope.variables[self.name]
        self.name = new_name

        # rename references
        for identifier in self.references:
            identifier.value = new_name

    def erase(self):
        assert self.name in self.scope.variables, f'fatal: symbol {self.name} not defined'
        del self.scope.variables[self.name]


class SymbolTable:
    """
    A symbol table represents a lexical scope in the program.
    It maps symbol names to declaration information through symbols.
    """

    def __init__(self, parent: Optional['SymbolTable'] = None, boundary: bool = False):
        self.parent = parent  # represents the scope this scope is nested within
        self.children: List[SymbolTable] = []  # represents the scopes nested within this scope
        self.boundary = boundary  # represents whether this scope is a boundary (e.g., at function definitions)
        self.variables: Dict[str, Symbol] = {}  # represents the variables declared in this scope

    def reset(self):
        self.children.clear()
        self.variables.clear()

    def enclosing_boundary(self) -> Optional['SymbolTable']:
        if self.parent is None:
            return None
        elif self.parent.boundary:
            return self.parent
        else:
            return self.parent.enclosing_boundary()

    def lookup(self, name: str, recursive: bool = True, ignore_boundary: bool = False) -> Optional[Symbol]:
        if name in self.variables:
            return self.variables[name]
        elif recursive and self.parent is not None and (ignore_boundary or not self.boundary):
            return self.parent.lookup(name, True, ignore_boundary)
        else:
            return None

    def register(self, name: str, extern: bool = False, node: Optional['AbstractNode'] = None, type: Optional['TypeNode'] = None) -> Symbol:
        assert name not in self.variables, f'fatal: symbol {name} already defined'
        symbol = Symbol(name, self, extern, node, type)
        self.variables[name] = symbol
        return symbol

    def open_scope(self, boundary: bool = False):
        scope = SymbolTable(self, boundary=boundary)
        self.children.append(scope)
        return scope

    def close_scope(self):
        parent = self.parent
        assert parent is not None, 'fatal: scope underflow'
        return parent
