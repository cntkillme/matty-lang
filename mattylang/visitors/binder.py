from mattylang.ast import *
from mattylang.module import Module
from mattylang.symbols import SymbolTable
from mattylang.visitor import AbstractVisitor


class Binder(AbstractVisitor):
    def __init__(self, module: Module):
        self.module = module
        self.__active_scope = module.globals
        self.__parent_chunk: Optional[ChunkNode] = None
        self.__undefined_references: dict[IdentifierNode, SymbolTable] = {}

    def visit_chunk(self, node: ChunkNode):
        assert node.scope is None, f'fatal: {node} already has symbol table: {node.scope}'
        node.parent_chunk = self.__parent_chunk
        self.__parent_chunk = node
        self.__active_scope = self.__active_scope.open_scope()
        node.scope = self.__active_scope
        super().visit_chunk(node)  # visit children

        # handle undefined references
        for identifier in self.__undefined_references:
            if identifier.symbol is None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'analysis: undefined reference {identifier.value}', identifier.position)

        self.__undefined_references.clear()
        self.__parent_chunk = node.parent_chunk
        self.__active_scope = self.__active_scope.close_scope()

    def visit_variable_definition(self, node: VariableDefinitionNode):
        # check for duplicate definition
        symbol = self.__active_scope.lookup(node.identifier.value, False)
        if symbol is not None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of {node.identifier.value}', node.identifier.position)

        node.initializer.accept(self)

        # register symbol after vising the initializer
        if symbol is None:
            self.__active_scope.register(node.identifier.value, node=node)
            node.identifier.accept(self)

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        # check for duplicate definition
        symbol = self.__active_scope.lookup(node.identifier.value, False)
        if symbol is not None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of {node.identifier.value}', node.identifier.position)
        else:
            # register symbol
            self.__active_scope.register(node.identifier.value, node=node)
            node.identifier.accept(self)

        # visit children in new boundary scope
        self.__active_scope = self.__active_scope.open_scope(boundary=True)
        for parameter in node.parameters:
            parameter.accept(self)
        node.body.accept(self)
        self.__active_scope = self.__active_scope.close_scope()

        # unset function body's parent chunk
        node.body.parent_chunk = None

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
