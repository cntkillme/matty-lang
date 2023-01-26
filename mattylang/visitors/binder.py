from mattylang.module import Module
from mattylang.nodes import *
from mattylang.symbols import SymbolTable
from mattylang.visitor import AbstractVisitor


class Binder(AbstractVisitor):
    def __init__(self, module: Module):
        self.module = module
        self.__active_scope = module.globals
        self.__undefined_references: dict[IdentifierNode, SymbolTable] = {}

    def visit_chunk(self, node: ChunkNode):
        assert node.symbol_table is None, f'fatal: {node} already has {node.symbol_table}'
        self.__active_scope = self.__active_scope.open_scope()
        node.symbol_table = self.__active_scope
        super().visit_chunk(node)  # visit children

        for identifier in self.__undefined_references:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: undefined variable {identifier.value}', identifier.position)

        self.__undefined_references.clear()
        self.__active_scope = self.__active_scope.close_scope()

    def visit_variable_definition(self, node: VariableDefinitionNode):
        node.initializer.accept(self)  # visit initializer

        if self.__active_scope.lookup(node.identifier.value, False) is not None:
            node.invalid = True
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of variable {node.identifier.value}', node.identifier.position)
            return

        self.__active_scope.register(node)  # register variable in current scope
        node.identifier.accept(self)  # visit identifier

    def visit_identifier(self, node: IdentifierNode):
        assert node.symbol is None, f'fatal: {node} already has {node.symbol}'
        symbol = self.__active_scope.lookup(node.value, True)

        if symbol is not None:
            node.symbol = symbol
            node.symbol.references.append(node)
        else:
            node.invalid = True
            self.__mark_undefined_reference(node, self.__active_scope)

    def __mark_undefined_reference(self, identifier: IdentifierNode, scope: SymbolTable):
        assert identifier not in self.__undefined_references, f'fatal: duplicate undefined reference {identifier.value}'
        self.__undefined_references[identifier] = scope
