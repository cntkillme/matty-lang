from mattylang.module import Module
from mattylang.nodes import *
from mattylang.visitor import ScopedVisitor


class Emitter(ScopedVisitor):
    def __init__(self, module: Module):
        super().__init__(module)
        self.__lines = list[str]()
        self.__statement: str = ''
        self.__depth: int = 0
        self.__renamed = set[AbstractNode]()

    def __str__(self):
        return '\n'.join(self.__lines)

    def __write_line(self, stmt: str):
        self.__lines.append(stmt)

    def visit_program(self, node: ProgramNode):
        assert not node.invalid, 'invalid program'
        super().visit_program(node)

    def visit_chunk(self, node: ChunkNode):

        # add suffix to names to avoid collisions
        for statement in node.statements:
            if isinstance(statement, VariableDefinitionNode) and not statement in self.__renamed:
                symbol = statement.identifier.symbol
                if symbol is not None:
                    name = statement.identifier.value
                    new_name = f'{name}_{self.__depth}'

                    # append underscores while there is a collision
                    while symbol.scope.lookup(new_name, True) is not None:
                        new_name += '_'

                    statement.identifier.value = new_name
                    symbol.scope.symbols[new_name] = symbol
                    del symbol.scope.symbols[name]

                    for identifier in symbol.references:
                        identifier.value = new_name

                    self.__renamed.add(statement)

        self.__depth += 1
        super().visit_chunk(node)
        self.__depth -= 1

    def visit_variable_definition(self, node: VariableDefinitionNode):
        self.__statement = f'{node.identifier.value} = '
        node.initializer.accept(self)
        self.__write_line(self.__statement)

    def visit_variable_assignment(self, node: VariableAssignmentNode):
        self.__statement = f'{node.identifier.value} = '
        node.value.accept(self)
        self.__write_line(self.__statement)

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
