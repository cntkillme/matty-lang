from mattylang.ast import *
from mattylang.module import Module
from mattylang.symbols import SymbolTable
from mattylang.visitor import AbstractVisitor


class AstPrinter(AbstractVisitor):
    def __init__(self, module: Module, indent: int = 0):
        super().__init__()
        self.module = module
        self.indent = indent

    def visit_program(self, node: ProgramNode):
        self.__header(node)
        self.indent += 1
        super().visit_program(node)
        self.indent -= 1

    def visit_chunk(self, node: ChunkNode):
        self.__header(node)
        self.indent += 1
        super().visit_chunk(node)
        self.indent -= 1

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__header(node)
        self.indent += 1
        super().visit_variable_definition(node)
        self.indent -= 1

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        self.__header(node)
        self.indent += 1
        super().visit_variable_assignment(node)
        self.indent -= 1

    def visit_if_statement(self, node: IfStatementNode):
        self.__header(node)
        self.indent += 1
        super().visit_if_statement(node)
        self.indent -= 1

    def visit_while_statement(self, node: WhileStatementNode):
        self.__header(node)
        self.indent += 1
        super().visit_while_statement(node)
        self.indent -= 1

    def visit_break_statement(self, node: BreakStatementNode):
        self.__header(node)

    def visit_continue_statement(self, node: ContinueStatementNode):
        self.__header(node)

    def visit_function_definition(self, node: FunctionDefinitionNode):
        self.__header(node)
        self.indent += 1
        super().visit_function_definition(node)

        node.identifier.accept(self)
        self.indent += 1
        for parameter in node.parameters:
            parameter.accept(self)
        self.indent -= 1
        node.body.accept(self)

        self.indent -= 1

    def visit_function_parameter(self, node: FunctionParameterNode):
        self.__header(node)
        self.indent += 1
        super().visit_function_parameter(node)
        self.indent -= 1

    def visit_return_statement(self, node: ReturnStatementNode):
        self.__header(node)
        self.indent += 1
        super().visit_return_statement(node)
        self.indent -= 1

    def visit_call_statement(self, node: CallStatementNode):
        self.__header(node)
        self.indent += 1
        super().visit_call_statement(node)
        self.indent += 1

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
        self.indent += 1
        super().visit_call_expression(node)
        self.indent -= 1

    def visit_unary_expression(self, node: UnaryExpressionNode):
        self.__header(node)
        self.indent += 1
        super().visit_unary_expression(node)
        self.indent -= 1

    def visit_binary_expression(self, node: BinaryExpressionNode):
        self.__header(node)
        self.indent += 1
        super().visit_binary_expression(node)
        self.indent -= 1

    def visit_nil_type(self, node: NilTypeNode):
        self.__header(node)

    def visit_bool_type(self, node: BoolTypeNode):
        self.__header(node)

    def visit_real_type(self, node: RealTypeNode):
        self.__header(node)

    def visit_string_type(self, node: StringTypeNode):
        self.__header(node)

    def visit_function_type(self, node: FunctionTypeNode):
        self.__header(node)

    def __write(self, text: str):
        print('  ' * self.indent + text)

    def __header(self, node: AbstractNode):
        line, column = self.module.line_map.get_location(node.position)
        self.__write(f'{node} <{line}, {column}>')

        if isinstance(node, IdentifierNode):
            self.__write(f'- symbol: {node.symbol}')

        if isinstance(node, ExpressionNode):
            self.__write(f'- type: {node.type}')


class SymbolPrinter:
    def __init__(self, module: Module, indent: int = 0):
        super().__init__()
        self.module = module
        self.__indent = indent
        self.__write_scope(module.globals)

    def __write(self, text: str):
        print('  ' * self.__indent + text)

    def __write_scope(self, scope: SymbolTable):
        if scope.boundary:
            self.__write('{')

        for symbol in scope.variables.values():
            if symbol.node:
                line, column = self.module.line_map.get_location(symbol.node.position)
                self.__write(f'{str(symbol)} <{line}, {column}>')
            else:
                self.__write(str(symbol))

        for child in scope.children:
            self.__indent += 1
            self.__write_scope(child)
            self.__indent -= 1

        if scope.boundary:
            self.__write('}')
