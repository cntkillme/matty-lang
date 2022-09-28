from typing import Dict
from compiler.nodes import *
from compiler.scope import Scope
from compiler.visitor import AbstractVisitor


class Binder(AbstractVisitor):
    def __init__(self, global_scope: Scope):
        self.__global_scope: Scope = global_scope
        self.__active_scope: Scope = global_scope
        self.__forward_references: Dict[IdentifierNode, Scope] = {}

    def get_global_scope(self):
        return self.__global_scope

    def visit_program(self, program: ProgramNode):
        self.visit_chunk(program.get_chunk())

    def visit_chunk(self, chunk: ChunkNode):
        self.__active_scope = self.__active_scope.open_scope()
        chunk.set_scope(self.__active_scope)

        for statement in chunk.get_statements():
            self.visit_statement(statement)

        for identifier, scope in self.__forward_references.items():
            symbol = scope.get_symbol(identifier.get_text(), True)
            if symbol is None:
                raise ValueError('undeclared identifier', identifier.get_text())
            identifier.set_symbol(symbol)
            # they will remain declared forward references
            # example: `def x = y def y = 0`, the first `y` is a declared forward reference

        self.__forward_references.clear()
        self.__active_scope = self.__active_scope.close_scope()

    def visit_variable_definition(self, variable_definition: VariableDefinitionNode):
        name, value = variable_definition.get_name(), variable_definition.get_value()
        self.visit_identifier(name)
        self.visit_expression(value)

        # if symbol already exists in this scope, it's a duplicate declaration
        if self.__active_scope.get_symbol(name.get_text(), False) is not None:
            raise ValueError('duplicate declaration', name.get_text())

        symbol = self.__active_scope.add_symbol(name.get_text(), variable_definition)
        name.set_symbol(symbol)
        self.__clear_undeclared_identifier(name)

    def visit_identifier(self, identifier: IdentifierNode):
        symbol = self.__active_scope.get_symbol(identifier.get_text(), True)
        if symbol is not None:
            identifier.set_symbol(symbol)
        else:
            identifier.set_forward_reference(True)
            self.__set_undeclared_identifier(identifier, self.__active_scope)

    def __set_undeclared_identifier(self, identifier: IdentifierNode, scope: Scope):
        assert identifier not in self.__forward_references, f'fatal: duplicate identifier {identifier.get_text()}'
        self.__forward_references[identifier] = scope

    def __clear_undeclared_identifier(self, identifier: IdentifierNode):
        if identifier in self.__forward_references:
            del self.__forward_references[identifier]
