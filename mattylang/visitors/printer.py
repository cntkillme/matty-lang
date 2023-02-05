from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import AbstractVisitor, ScopedVisitor


class Printer(AbstractVisitor):
    def __init__(self, module: Module, indent: int = 0):
        super().__init__()
        self.module = module
        self.__indent = indent

    def visit_program(self, node: ProgramNode):
        self.__header(node)
        self.__indent += 1
        super().visit_program(node)
        self.__indent -= 1

    def visit_chunk(self, node: ChunkNode):
        self.__header(node)
        self.__indent += 1
        super().visit_chunk(node)
        self.__indent -= 1

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_variable_definition(node)
        self.__indent -= 1

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        self.__header(node)
        self.__indent += 1
        super().visit_variable_assignment(node)
        self.__indent -= 1

    def visit_if_statement(self, node: IfStatementNode):
        self.__header(node)
        self.__indent += 1
        super().visit_if_statement(node)
        self.__indent -= 1

    def visit_while_statement(self, node: WhileStatementNode):
        self.__header(node)
        self.__indent += 1
        super().visit_while_statement(node)
        self.__indent -= 1

    def visit_break_statement(self, node: BreakStatementNode):
        self.__header(node)

    def visit_continue_statement(self, node: ContinueStatementNode):
        self.__header(node)

    def visit_function_definition(self, node: FunctionDefinitionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_function_definition(node)
        self.__indent -= 1

    def visit_return_statement(self, node: ReturnStatementNode):
        self.__header(node)
        self.__indent += 1
        super().visit_return_statement(node)
        self.__indent -= 1

    def visit_call_statement(self, node: CallStatementNode):
        self.__header(node)
        self.__indent += 1
        super().visit_call_statement(node)
        self.__indent += 1

    def visit_unary_expression(self, node: UnaryExpressionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_unary_expression(node)
        self.__indent -= 1

    def visit_binary_expression(self, node: BinaryExpressionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_binary_expression(node)
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

    def visit_call_expression(self, node: CallExpressionNode):
        self.__header(node)
        self.__indent += 1
        super().visit_call_expression(node)
        self.__indent -= 1

    def __write(self, text: str):
        print('  ' * self.__indent + text)

    def __header(self, node: AbstractNode):
        line, column = self.module.line_map.get_location(node.position)
        src_ctx = f'<{line}, {column}>'

        if node.invalid:
            self.__write(f'\u001b[41m{node}\u001b[0m {src_ctx}')
        else:
            self.__write(f'{node} {src_ctx}')


class SymbolPrinter(ScopedVisitor):
    def __init__(self, module: Module, indent: int = 0):
        super().__init__(module)
        self.__indent = indent

    def visit_program(self, node: ProgramNode):
        super().visit_program(node)

    def visit_chunk(self, node: ChunkNode):
        self.__write('{')
        self.__indent += 1

        if node.symbol_table is not None:
            for symbol in node.symbol_table.symbols.values():
                self.__write(str(symbol))

        super().visit_chunk(node)
        self.__indent -= 1
        self.__write('}')

    def __write(self, text: str):
        print('  ' * self.__indent + text)
