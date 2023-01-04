from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mattylang.module import Module

if TYPE_CHECKING:
    from mattylang.nodes import *


class AbstractVisitor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def visit_program(self, node: 'ProgramNode'):
        self.visit_chunk(node.chunk)
        node.invalid = node.invalid or node.chunk.invalid

    def visit_chunk(self, node: 'ChunkNode'):
        for statement in node.statements:
            statement.accept(self)
            node.invalid = node.invalid or statement.invalid

    def visit_variable_definition(self, node: 'VariableDefinitionNode'):
        node.identifier.accept(self)
        node.initializer.accept(self)
        node.invalid = node.invalid or node.identifier.invalid or node.initializer.invalid

    def visit_variable_assignment(self, node: 'VariableAssignmentNode'):
        node.identifier.accept(self)
        node.value.accept(self)
        node.invalid = node.invalid or node.identifier.invalid or node.value.invalid

    def visit_unary_expression(self, node: 'UnaryExpressionNode'):
        node.operand.accept(self)
        node.invalid = node.invalid or node.operand.invalid

    def visit_binary_expression(self, node: 'BinaryExpressionNode'):
        node.left.accept(self)
        node.right.accept(self)
        node.invalid = node.invalid or node.left.invalid or node.right.invalid

    def visit_nil_literal(self, node: 'NilLiteralNode'):
        pass

    def visit_bool_literal(self, node: 'BoolLiteralNode'):
        pass

    def visit_real_literal(self, node: 'RealLiteralNode'):
        pass

    def visit_string_literal(self, node: 'StringLiteralNode'):
        pass

    def visit_identifier(self, node: 'IdentifierNode'):
        pass


class ScopedVisitor(AbstractVisitor, ABC):
    def __init__(self, module: Module):
        self.module = module
        self._globals = module.globals
        self._scope = module.globals

    def visit_program(self, node: 'ProgramNode'):
        assert node.chunk.symbol_table and node.chunk.symbol_table.parent == self._globals, 'fatal: global scope mismatch'
        super().visit_program(node)

    def visit_chunk(self, node: 'ChunkNode'):
        assert node.symbol_table and node.symbol_table.parent == self._scope, 'fatal: scope parent mismatch'
        scope = self._scope
        self._scope = node.get_symbol_table()
        super().visit_chunk(node)
        self._scope = scope
