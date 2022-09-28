from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from compiler.nodes import VariableDefinitionNode


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.__parent = parent
        self.__symbols: Dict[str, Symbol] = {}
        self.__children: List[Scope] = []

    def get_symbols(self):
        return self.__symbols

    def get_symbol(self, name: str, recursive: bool) -> Optional['Symbol']:
        if name in self.__symbols:
            return self.__symbols[name]
        elif recursive and self.__parent is not None:
            return self.__parent.get_symbol(name, True)
        else:
            return None

    def add_symbol(self, name: str, value_declaration: Optional['VariableDefinitionNode'] = None):
        assert name not in self.__symbols
        symbol = Symbol(self, name, value_declaration)
        self.__symbols[name] = symbol
        return symbol

    def get_parent(self):
        return self.__parent

    def set_parent(self, parent: 'Scope'):
        assert self.__parent is None
        self.__parent = parent

    def get_children(self):
        return self.__children

    def open_scope(self) -> 'Scope':
        scope = Scope(self)
        self.__children.append(scope)
        return scope

    def close_scope(self) -> 'Scope':
        assert self.__parent is not None
        return self.__parent


class Symbol():
    def __init__(self, scope: Scope, name: str, value_declaration: Optional['VariableDefinitionNode'] = None):
        self.__scope = scope
        self.__name = name
        self.__value_declaration: Optional['VariableDefinitionNode'] = None

        if value_declaration is not None:
            self.set_value_declaration(value_declaration)

    def get_scope(self):
        return self.__scope

    def get_name(self):
        return self.__name

    def get_value_declaration(self):
        assert self.__value_declaration is not None
        return self.__value_declaration

    def set_value_declaration(self, declaration: 'VariableDefinitionNode'):
        assert self.__value_declaration is None
        self.__value_declaration = declaration
