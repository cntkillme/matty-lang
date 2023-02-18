from abc import ABC, abstractmethod
from typing import Callable, cast, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mattylang.symbols import Symbol, SymbolTable
    from mattylang.visitor import AbstractVisitor


class AbstractNode(ABC):
    @abstractmethod
    def __init__(self, position: int):
        self.parent: Optional[AbstractNode] = None
        self.position = position

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def accept(self, visitor: 'AbstractVisitor') -> None:
        pass

    def get_first_ancestor(self, predicate: Callable[['AbstractNode'], bool]) -> Optional['AbstractNode']:
        node = self.parent
        while node is not None:
            if predicate(node):
                return node
            node = node.parent
        return None


class ProgramNode(AbstractNode):
    def __init__(self, chunk: 'ChunkNode', position: int = -1):
        super().__init__(position)
        self.chunk = chunk
        chunk.parent = self

    def __str__(self):
        return f'program'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_program(self)


class StatementNode(AbstractNode, ABC):
    pass


class ChunkNode(StatementNode):
    def __init__(self, statements: List[StatementNode] = [], position: int = -1):
        super().__init__(position)
        self.statements = statements
        self.symbol_table: Optional[SymbolTable] = None  # set by the binder
        self.return_type: Optional['TypeNode'] = None  # set by the checker
        for statement in statements:
            statement.parent = self

    def __str__(self):
        return f'chunk'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_chunk(self)

    def get_symbol_table(self) -> 'SymbolTable':
        assert self.symbol_table is not None, f'fatal: symbol table for {self} not set, was the binder run?'
        return self.symbol_table


class VariableDefinitionNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', initializer: 'ExpressionNode', position: int = -1):
        super().__init__(position)
        self.identifier, self.initializer = identifier, initializer
        identifier.parent, initializer.parent = self, self

    def __str__(self):
        return f'variable_definition'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_definition(self)


class VariableAssignmentNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', value: 'ExpressionNode', position: int = -1):
        super().__init__(position)
        self.identifier, self.value = identifier, value
        identifier.parent, value.parent = self, self

    def __str__(self):
        return f'variable_assignment'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_variable_assignment(self)


class IfStatementNode(StatementNode):
    def __init__(self, condition: 'ExpressionNode', if_body: ChunkNode, else_body: Optional[ChunkNode] = None, position: int = -1):
        super().__init__(position)
        self.condition, self.if_body, self.else_body = condition, if_body, else_body
        if_body.parent = self
        if else_body is not None:
            else_body.parent = self

    def __str__(self):
        return f'if_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_if_statement(self)


class WhileStatementNode(StatementNode):
    def __init__(self, condition: 'ExpressionNode', body: ChunkNode, position: int = -1):
        super().__init__(position)
        self.condition, self.body = condition, body
        condition.parent, body.parent = self, self

    def __str__(self):
        return f'while_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_while_statement(self)


class BreakStatementNode(StatementNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self):
        return f'break_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_break_statement(self)

    def get_enclosing_loop_statement(self):
        return cast(Optional[WhileStatementNode], self.get_first_ancestor(lambda parent: isinstance(parent, WhileStatementNode)))


class ContinueStatementNode(StatementNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self):
        return f'continue_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_continue_statement(self)

    def get_enclosing_loop_statement(self):
        return cast(Optional[WhileStatementNode], self.get_first_ancestor(lambda parent: isinstance(parent, WhileStatementNode)))


class FunctionDefinitionNode(StatementNode):
    def __init__(self, identifier: 'IdentifierNode', parameters: List['FunctionParameterNode'], body: ChunkNode, position: int = -1):
        super().__init__(position)
        self.identifier, self.parameters, self.body = identifier, parameters, body
        identifier.parent, body.parent = self, self
        for parameter in parameters:
            parameter.parent = self

    def __str__(self):
        return f'function_definition'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_function_definition(self)


class FunctionParameterNode(AbstractNode):
    def __init__(self, identifier: 'IdentifierNode', type: 'TypeNode', position: int = -1):
        super().__init__(position)
        self.identifier, self.type = identifier, type
        identifier.parent, type.parent = self, self

    def __str__(self):
        return f'variable_declaration'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_function_parameter(self)


class ReturnStatementNode(StatementNode):
    def __init__(self, value: Optional['ExpressionNode'] = None, position: int = -1):
        super().__init__(position)
        self.value = value
        if value is not None:
            value.parent = self

    def __str__(self):
        return f'return_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_return_statement(self)

    def get_enclosing_function_definition(self):
        return cast(Optional[FunctionDefinitionNode], self.get_first_ancestor(lambda parent: isinstance(parent, FunctionDefinitionNode)))


class CallStatementNode(StatementNode):
    def __init__(self, call_expression: 'CallExpressionNode', position: int = -1):
        super().__init__(position)
        self.call_expression = call_expression
        call_expression.parent = self

    def __str__(self):
        return f'call_statement'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_call_statement(self)


class ExpressionNode(AbstractNode, ABC):
    @ abstractmethod
    def __init__(self, position: int = -1):
        super().__init__(position)
        self.type: Optional[TypeNode] = None  # set by the checker

    def get_type(self) -> 'TypeNode':
        assert self.type is not None, f'fatal: type for {self} not set, was the checker run?'
        return self.type


class PrimaryExpressionNode(ExpressionNode, ABC):
    pass


class NilLiteralNode(PrimaryExpressionNode):
    def __init__(self, position: int = -1):
        super().__init__(position)
        self.value = None

    def __str__(self):
        return 'nil_literal'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_nil_literal(self)

    def get_type(self) -> 'NilTypeNode':
        return NilTypeNode()


class BoolLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: bool, position: int = -1):
        super().__init__(position)
        self.value = value

    def __str__(self):
        return f'bool_literal({str(self.value).lower()})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_bool_literal(self)

    def get_type(self) -> 'BoolTypeNode':
        return BoolTypeNode()


class RealLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: float, position: int = -1):
        super().__init__(position)
        self.value = value

    def __str__(self):
        return f'real_literal({self.value})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_real_literal(self)

    def get_type(self) -> 'RealTypeNode':
        return RealTypeNode()


class StringLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: str, position: int = -1):
        super().__init__(position)
        self.value = value

    def __str__(self):
        return f'string_literal({repr(self.value)})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_string_literal(self)

    def get_type(self) -> 'StringTypeNode':
        return StringTypeNode()


class IdentifierNode(PrimaryExpressionNode):
    def __init__(self, value: str, position: int = -1):
        super().__init__(position)
        self.value = value
        self.symbol: Optional['Symbol'] = None  # set by the binder

    def __str__(self):
        return f'identifier({self.value})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_identifier(self)

    def get_type(self) -> 'TypeNode':
        return self.get_symbol().get_type()

    def get_symbol(self) -> 'Symbol':
        assert self.symbol is not None, f'fatal: symbol not set for {self}, was the binder run?'
        return self.symbol


class CallExpressionNode(PrimaryExpressionNode):
    def __init__(self, identifier: IdentifierNode, arguments: List[ExpressionNode], position: int = -1):
        super().__init__(position)
        self.identifier, self.arguments = identifier, arguments
        self.symbol: Optional[Symbol] = None  # set by the binder
        self.type: Optional[FunctionTypeNode] = None  # set by the checker
        identifier.parent = self
        for argument in arguments:
            argument.parent = self

    def __str__(self):
        return f'call_expression'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_call_expression(self)

    def get_type(self) -> 'TypeNode':
        return self.get_symbol().get_type()

    def get_symbol(self) -> 'Symbol':
        assert self.symbol is not None,  f'fatal: symbol not set for {self}, was the binder run?'
        return self.symbol


class UnaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode, position: int = -1):
        super().__init__(position)
        self.operator, self.operand = operator, operand
        operand.parent = self

    def __str__(self):
        return f'unary_expression({self.operator})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_unary_expression(self)

    def get_type(self) -> 'TypeNode':
        return self.operand.get_type()


class BinaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, left: ExpressionNode, right: ExpressionNode, position: int = -1):
        super().__init__(position)
        self.operator, self.left, self.right = operator, left, right
        left.parent, right.parent = self, self

    def __str__(self):
        return f'binary_expression({self.operator})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_binary_expression(self)

    def get_type(self) -> 'TypeNode':
        if self.operator in ('+', '-', '*', '/', '%'):
            return self.left.get_type()
        elif self.operator in ('==', '!=', '<', '<=', '>', '>=', '||', '&&'):
            return BoolTypeNode()
        else:
            assert False, f'fatal: unknown binary operator {self.operator}'


class TypeNode(AbstractNode, ABC):
    @ abstractmethod
    def is_assignable_to(self, other: 'TypeNode') -> bool:
        pass

    def is_equivalent(self, other: 'TypeNode') -> bool:
        return self.is_assignable_to(other) and other.is_assignable_to(self)


class AnyTypeNode(TypeNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self) -> str:
        return 'Any'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        assert False, 'fatal: any type should not be visited'

    def is_assignable_to(self, other: TypeNode):
        return True


class PrimitiveTypeNode(TypeNode, ABC):
    def is_assignable_to(self, other: TypeNode):
        return isinstance(self, other.__class__) or isinstance(other, AnyTypeNode)


class NilTypeNode(PrimitiveTypeNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self) -> str:
        return 'Nil'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_nil_type(self)


class BoolTypeNode(PrimitiveTypeNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self) -> str:
        return 'Bool'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_bool_type(self)


class RealTypeNode(PrimitiveTypeNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self) -> str:
        return 'Real'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_real_type(self)


class StringTypeNode(PrimitiveTypeNode):
    def __init__(self, position: int = -1):
        super().__init__(position)

    def __str__(self) -> str:
        return 'String'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_string_type(self)


class FunctionTypeNode(TypeNode):
    def __init__(self, parameter_types: List[TypeNode], return_type: TypeNode, position: int = -1):
        super().__init__(position)
        self.parameter_types, self.return_type = parameter_types, return_type

    def __str__(self) -> str:
        return f'({(", ").join(map(str, self.parameter_types))}) -> {self.return_type}'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_function_type(self)

    def is_assignable_to(self, other: TypeNode) -> bool:
        # MattyLang v1.0 does not support sub-typing, so the function signatures must be identical.
        if not isinstance(other, FunctionTypeNode):
            return isinstance(other, AnyTypeNode)
        elif not self.return_type.is_assignable_to(other.return_type):
            return False
        elif len(self.parameter_types) != len(other.parameter_types):
            return False
        else:
            for i in range(len(self.parameter_types)):
                if not other.parameter_types[i].is_assignable_to(self.parameter_types[i]):
                    return False

        return True
