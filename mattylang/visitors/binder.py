from mattylang.ast import *
from mattylang.module import Module
from mattylang.symbols import SymbolTable
from mattylang.visitor import AbstractVisitor


class Binder(AbstractVisitor):
    def __init__(self, module: Module):
        self.module = module
        self.__active_scope = module.globals
        self.__undefined_references: dict[IdentifierNode, SymbolTable] = {}

    def visit_chunk(self, node: ChunkNode):
        assert node.symbol_table is None, f'fatal: {node} already has symbol table: {node.symbol_table}'
        self.__active_scope = self.__active_scope.open_scope()
        node.symbol_table = self.__active_scope

        # visit children
        super().visit_chunk(node)

        # handle undefined references
        for identifier in self.__undefined_references:
            # TODO: allow forward references to functions
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: undefined variable {identifier.value}', identifier.position)

        self.__undefined_references.clear()
        self.__active_scope = self.__active_scope.close_scope()

    def visit_variable_definition(self, node: VariableDefinitionNode):
        # visit the initializer first, as a variable cannot reference itself
        node.initializer.accept(self)

        # register symbol
        if self.__active_scope.lookup(node.identifier.value, False) is not None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of {node.identifier.value}', node.identifier.position)
            return

        # TODO: create declaration and symbol

        node.identifier.accept(self)

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        # register declaration/symbol first, to allow recursion
        if self.__active_scope.lookup(node.identifier.value, False) is not None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of {node.identifier.value}', node.identifier.position)
            return

        self.__active_scope = self.__active_scope.open_scope()

        # visit children
        super().visit_function_definition(node)

    # binds symbols to identifiers, and marks undefined/yet-to-be-defined references
    def visit_identifier(self, node: IdentifierNode):
        assert node.symbol is None, f'fatal: {node} already has symbol: {node.symbol}'
        symbol = self.__active_scope.lookup(node.value, True)

        if symbol is not None:
            node.symbol = symbol
        else:
            self.__mark_undefined_reference(node, self.__active_scope)

    def __mark_undefined_reference(self, identifier: IdentifierNode, scope: SymbolTable):
        assert identifier not in self.__undefined_references, f'fatal: duplicate undefined reference {identifier.value}'
        self.__undefined_references[identifier] = scope
