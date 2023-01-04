from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import ScopedVisitor


class Printer(ScopedVisitor):
    def __init__(self, module: Module, indent: int = 0):
        super().__init__(module)
        self.__indent = indent

    def visit_program(self, node: ProgramNode):
        self.__header(node)
        self.__indent += 1
        super().visit_program(node)
        self.__indent -= 1

    def visit_chunk(self, node: ChunkNode):
        self.__header(node)
        self.__indent += 1
        self.__write('scope: ' + str(node.symbol_table)
                     if node.symbol_table is not None else '\u001b[41m<no scope>\u001b[0m')
        super().visit_chunk(node)  # visit children
        self.__indent -= 1

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_variable_definition(node)  # visit children
        self.__indent -= 1

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        self.__header(node)
        self.__indent += 1
        super().visit_variable_assignment(node)  # visit children
        self.__indent -= 1

    def visit_unary_expression(self, node: UnaryExpressionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_unary_expression(node)  # visit children
        self.__indent -= 1

    def visit_binary_expression(self, node: BinaryExpressionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_binary_expression(node)  # visit children
        self.__indent -= 1

    def visit_nil_literal(self, node: NilLiteralNode):
        self.__header(node)

    def visit_bool_literal(self, node: BoolLiteralNode):
        self.__header(node)

    def visit_real_literal(self, node: RealLiteralNode):
        self.__header(node)

    def visit_string_literal(self, node: StringLiteralNode):
        self.__header(node)

    def visit_identifier(self, node: IdentifierNode):
        self.__header(node)
        self.__indent += 1
        self.__write('symbol: ' + (str(node.symbol) if node.symbol is not None else '\u001b[41m<no symbol>\u001b[0m'))
        self.__write('type  : ' + (str(node.type) if node.type is not None else '\u001b[41m<no type>\u001b[0m'))
        self.__indent -= 1

    def __write(self, text: str):
        print('  ' * self.__indent + text)

    def __header(self, node: AbstractNode):
        if node.invalid:
            self.__write(f'\u001b[41m{node}\u001b[0m')
        else:
            self.__write(f'{node}')


class SymbolPrinter(ScopedVisitor):
    def __init__(self, module: Module, indent: int = 0):
        super().__init__(module)
        self.__indent = indent

    def visit_program(self, node: 'ProgramNode'):
        super().visit_program(node)

    def visit_chunk(self, node: ChunkNode):
        self.__write('{')
        self.__indent += 1

        if node.symbol_table is not None:
            for symbol in node.symbol_table.symbols.values():
                self.__write(str(symbol))

        super().visit_chunk(node)  # visit children
        self.__indent -= 1
        self.__write('}')

    def __write(self, text: str):
        print('  ' * self.__indent + text)
