from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Optional

from mattylang.ast.core import AbstractNode

if TYPE_CHECKING:
    from mattylang.ast.type import TypeNode
    from mattylang.symbols import Symbol
    from mattylang.visitor import AbstractVisitor


class ExpressionNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.type: Optional['TypeNode'] = None

    def get_type(self) -> 'TypeNode':
        assert self.type is not None, 'fatal: type not set'
        return self.type


class PrimaryExpressionNode(ExpressionNode, ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.value = None


class UnaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode):
        super().__init__()
        self.operator = operator
        operand.parent = self
        self.operand = operand
        self.invalid = operand.invalid

    def __str__(self):
        return f'unary_expression({self.operator})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_unary_expression(self)


class BinaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, left: ExpressionNode, right: ExpressionNode):
        super().__init__()
        self.operator = operator
        left.parent = self
        self.left = left
        right.parent = self
        self.right = right
        self.invalid = left.invalid or right.invalid

    def __str__(self):
        return f'binary_expression({self.operator})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_binary_expression(self)


class NilLiteralNode(PrimaryExpressionNode):
    def __init__(self):
        super().__init__()
        self.value = None

    def __str__(self):
        return 'nil_literal'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_nil_literal(self)


class BoolLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: bool):
        super().__init__()
        self.value = value

    def __str__(self):
        return f'bool_literal({str(self.value).lower()})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_bool_literal(self)


class RealLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def __str__(self):
        return f'real_literal({self.value})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_real_literal(self)


class StringLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def __str__(self):
        return f'string_literal({repr(self.value)})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_string_literal(self)


class IdentifierNode(PrimaryExpressionNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value
        self.symbol: Optional['Symbol'] = None

    def __str__(self):
        return f'identifier({self.value})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_identifier(self)


class CallExpressionNode(PrimaryExpressionNode):
    def __init__(self, target: IdentifierNode, arguments: List[ExpressionNode]):
        super().__init__()
        target.parent = self
        self.identifier = target
        for argument in arguments:
            argument.parent = self
        self.arguments = arguments

    def __str__(self):
        return f'call_expression({self.identifier.value})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_call_expression(self)
