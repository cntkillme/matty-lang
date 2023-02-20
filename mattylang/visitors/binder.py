from typing import Dict, Optional

from mattylang.ast import *
from mattylang.module import Module
from mattylang.symbols import SymbolTable
from mattylang.visitor import AbstractVisitor


class Binder(AbstractVisitor):
    def __init__(self, module: Module):
        self.module = module
        self.__active_scope = module.globals
        self.__parent_chunk: Optional[ChunkNode] = None
        self.__undefined_references: Dict[IdentifierNode, SymbolTable] = {}

    def visit_chunk(self, node: ChunkNode):
        assert node.scope is None, f'fatal: {node} already has symbol table: {node.scope}'

        # enter scope
        self.__active_scope = self.__active_scope.open_scope()
        node.scope = self.__active_scope
        node.parent_chunk = self.__parent_chunk
        self.__parent_chunk = node

        super().visit_chunk(node)  # visit children

        # handle undefined references
        for identifier in self.__undefined_references:
            # allow a function to reference itself (recursion)
            function_definition = identifier.get_enclosing_function()

            if function_definition is not None and function_definition.identifier.value == identifier.value:
                symbol = function_definition.identifier.symbol
                if symbol:
                    identifier.symbol = symbol
                    symbol.references.append(identifier)

            if identifier.symbol is None:
                self.module.diagnostics.emit_diagnostic(
                    'error', f'analysis: undefined reference to {identifier.value}', identifier.position)

        # exit scope
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

    def visit_function_parameter(self, node: 'FunctionParameterNode'):
        # check for duplicate definition
        symbol = self.__active_scope.lookup(node.identifier.value, False)
        if symbol is not None:
            self.module.diagnostics.emit_diagnostic(
                'error', f'analysis: duplicate definition of {node.identifier.value}', node.identifier.position)

        node.type.accept(self)

        # register symbol
        if symbol is None:
            self.__active_scope.register(node.identifier.value, node=node)
            node.identifier.accept(self)

    # binds symbols to identifiers
    def visit_identifier(self, node: IdentifierNode):
        if node.value == '#invalid':
            return

        assert node.symbol is None, f'fatal: {node} already has symbol: {node.symbol}'
        symbol = self.__active_scope.lookup(node.value, True)

        if symbol is not None:
            node.symbol = symbol
            symbol.references.append(node)
        else:
            self.__undefined_references[node] = self.__active_scope
