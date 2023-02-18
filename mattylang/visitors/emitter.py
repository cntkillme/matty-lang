from mattylang.ast import *
from mattylang.module import Module
from mattylang.visitor import AbstractVisitor


# Renames variables to handle collisions of variables within the same function scope in Python.
# TODO(v2.0): handle collisions of variables that are named Python keywords
class PythonSafeVariableRenamer(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module

    def visit_variable_definition(self, node: VariableDefinitionNode):
        symbol = node.identifier.get_symbol()
        name = symbol.name
        new_name = name

        # generate a new variable name if the current name was previously used
        if symbol.scope.parent is not None:
            i = 1
            while symbol.scope.parent.lookup(new_name, True) is not None:
                new_name = f'{name}_{i}'
                i += 1

        # skip renaming if name is not previously used
        if name == new_name:
            return

        # rename the variable in the symbol table
        del symbol.scope.variables[name]
        symbol.scope.variables[new_name] = symbol
        symbol.name = new_name

        # rename the variable references
        for identifier in symbol.references:
            identifier.value = new_name

        self.module.diagnostics.emit_diagnostic(
            'info', f'emitter: renamed variable {name} to {new_name}', node.identifier.position)

        # visit children
        super().visit_variable_definition(node)

    # TODO: functions


class Emitter(AbstractVisitor):
    def __init__(self, module: Module):
        super().__init__()
        self.module = module
        self.__lines = list[str]()
        self.__statement: str = ''
        self.__depth: int = 0

        # TODO: Rename variables to avoid collisions with Python keywords.

    def __str__(self):
        return '\n'.join(self.__lines)

    def __write_line(self, stmt: str):
        self.__lines.append(('    ' * self.__depth) + stmt)

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
