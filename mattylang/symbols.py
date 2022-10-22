from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from mattylang.ast.statement import VariableDefinitionNode


class Scope:
    def __init__(self):
        self.parent: Optional['Scope'] = None
        self.children: List[Scope] = []
        self.symbols: Dict[str, Symbol] = {}

    def __str__(self):
        return f'scope({len(self.symbols)})'

    def __iter__(self):
        return self.symbols.values()

    def lookup(self, name: str, recursive: bool) -> Optional['Symbol']:
        if name in self.symbols:
            return self.symbols[name]
        elif recursive and self.parent is not None:
            return self.parent.lookup(name, True)
        else:
            return None

    def register(self, name: str, declaration: 'VariableDefinitionNode', immutable: bool = False) -> 'Symbol':
        assert name not in self.symbols, f'fatal: symbol {name} already defined in scope {self}'
        symbol = Symbol(self, name, declaration)
        self.symbols[name] = symbol
        return symbol

    def open_scope(self) -> 'Scope':
        scope = Scope()
        scope.parent = self
        self.children.append(scope)
        return scope

    def close_scope(self) -> 'Scope':
        assert self.parent is not None
        return self.parent


class Symbol:
    def __init__(self, scope: Scope, name: str, declaration: 'VariableDefinitionNode'):
        self.scope = scope
        self.name = name
        self.declaration = declaration

    def __str__(self):
        return f'symbol({self.name})'
