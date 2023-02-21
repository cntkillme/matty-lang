from mattylang.ast import *
from mattylang.module import Module
from mattylang.symbols import Symbol
from mattylang.visitor import AbstractVisitor


# Renames variables to handle collisions of variables within the same function scope in Python.
# TODO(v2.0): handle collisions of variables that are named Python keywords
class PythonSafeVariableRenamer(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module

    def __handle_declaration(self, symbol: Symbol):
        name = symbol.name
        new_name = name

        # generate a new variable name if the current name was previously used
        if symbol.scope.parent is not None and not symbol.scope.boundary:
            i = 1
            while symbol.scope.parent.lookup(new_name, True) is not None:
                new_name = f'{name}_{i}'
                i += 1

        # skip renaming if name is not previously used
        if name == new_name:
            return

        symbol.rename(new_name)
        self.module.diagnostics.emit_diagnostic(
            'info', f'emitter: renamed variable {name} to {new_name}', symbol.get_node().position)

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__handle_declaration(node.identifier.get_symbol())
        super().visit_variable_definition(node)

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        self.__handle_declaration(node.identifier.get_symbol())
        super().visit_function_definition(node)


class Emitter(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module
        self.__lines = list[str]()
        self.__statement: str = ''
        self.__depth: int = 0

    def __str__(self):
        return '\n'.join(self.__lines)

    def __write_line(self, stmt: str):
        self.__lines.append(('    ' * self.__depth) + stmt)

    def visit_program(self, node: 'ProgramNode'):
        # pass 1: rename variables to handle collisions of variables within the same function scope in Python
        node.accept(PythonSafeVariableRenamer(self.module))
        super().visit_program(node)

    def visit_chunk(self, node: 'ChunkNode'):
        if len(node.statements) == 0:
            self.__write_line('pass')
        else:
            super().visit_chunk(node)

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__statement = f'{node.identifier.value} = '
        node.initializer.accept(self)
        self.__write_line(self.__statement)

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        self.__statement = f'{node.identifier.value} = '
        node.value.accept(self)
        self.__write_line(self.__statement)

    def visit_if_statement(self, node: 'IfStatementNode'):
        self.__statement = 'if '
        node.condition.accept(self)
        self.__statement += ':'
        self.__write_line(self.__statement)
        self.__depth += 1
        node.if_body.accept(self)
        self.__depth -= 1
        if node.else_body is not None:
            self.__write_line('else:')
            self.__depth += 1
            node.else_body.accept(self)
            self.__depth -= 1

    def visit_while_statement(self, node: 'WhileStatementNode'):
        self.__statement = 'while '
        node.condition.accept(self)
        self.__statement += ':'
        self.__write_line(self.__statement)
        self.__depth += 1
        node.body.accept(self)
        self.__depth -= 1

    def visit_break_statement(self, node: 'BreakStatementNode'):
        self.__write_line('break')

    def visit_continue_statement(self, node: 'ContinueStatementNode'):
        self.__write_line('continue')

    def visit_function_definition(self, node: 'FunctionDefinitionNode'):
        self.__statement = f'def {node.identifier.value}('
        for i, param in enumerate(node.parameters):
            if i > 0:
                self.__statement += ', '
            param.accept(self)
        self.__statement += '):'
        self.__write_line(self.__statement)
        self.__depth += 1
        node.body.accept(self)
        self.__depth -= 1

    def visit_function_parameter(self, node: 'FunctionParameterNode'):
        self.__statement += node.identifier.value

    def visit_return_statement(self, node: 'ReturnStatementNode'):
        if node.value:
            self.__statement = 'return '
            node.value.accept(self)
        else:
            self.__statement = 'return'
        self.__write_line(self.__statement)

    def visit_call_statement(self, node: 'CallStatementNode'):
        self.__statement = ''
        super().visit_call_statement(node)
        self.__write_line(self.__statement)

    def visit_nil_literal(self, node: NilLiteralNode):
        self.__statement += 'None'

    def visit_bool_literal(self, node: BoolLiteralNode):
        self.__statement += str(node.value)

    def visit_real_literal(self, node: RealLiteralNode):
        self.__statement += str(node.value)

    def visit_string_literal(self, node: StringLiteralNode):
        self.__statement += repr(node.value)

    def visit_identifier(self, node: IdentifierNode):
        self.__statement += node.value

    def visit_call_expression(self, node: 'CallExpressionNode'):
        self.__statement += f'{node.identifier.value}('
        for i, arg in enumerate(node.arguments):
            if i > 0:
                self.__statement += ', '
            arg.accept(self)
        self.__statement += ')'

    def visit_unary_expression(self, node: UnaryExpressionNode):
        if node.operator == '!':
            self.__statement += '(not '
        else:
            self.__statement += f'({node.operator} '
        node.operand.accept(self)
        self.__statement += ')'

    def visit_binary_expression(self, node: BinaryExpressionNode):
        self.__statement += '('
        node.left.accept(self)

        if node.operator == '||':
            self.__statement += ' or '
        elif node.operator == '&&':
            self.__statement += ' and '
        else:
            self.__statement += f' {node.operator} '

        node.right.accept(self)
        self.__statement += ')'
