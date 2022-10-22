from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from mattylang.ast.core import AbstractNode

if TYPE_CHECKING:
    from mattylang.ast.type import TypeNode
    from mattylang.symbols import Symbol
    from mattylang.visitor import AbstractVisitor


class ExpressionNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)
        self.type: Optional['TypeNode'] = None


class PrimaryExpressionNode(ExpressionNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)
        self.value = None

    def __str__(self):
        return f'{self.kind}({str(self.value)})'


class UnaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode):
        super().__init__('unary_expression')
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
        super().__init__('binary_expression')
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
        super().__init__('nil_literal')
        self.value = None

    def __str__(self):
        return f'nil_literal'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_nil_literal(self)


class BoolLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: bool):
        super().__init__('bool_literal')
        self.value = value

    def __str__(self):
        return f'{self.kind}({"true" if self.value else "false"})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_bool_literal(self)


class RealLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: float):
        super().__init__('real_literal')
        self.value = value

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_real_literal(self)


class StringLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: str):
        super().__init__('string_literal')
        self.value = value

    def __str__(self):
        return f'{self.kind}({repr(self.value)})'

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_string_literal(self)


class IdentifierNode(PrimaryExpressionNode):
    def __init__(self, value: str):
        super().__init__('identifier')
        self.value = value
        self.symbol: Optional['Symbol'] = None

    def accept(self, visitor: 'AbstractVisitor'):
        visitor.visit_identifier(self)
