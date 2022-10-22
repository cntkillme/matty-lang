from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mattylang.ast.core import AbstractNode

if TYPE_CHECKING:
    from mattylang.visitor import AbstractVisitor


class TypeNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)

    @abstractmethod
    def is_equivalent(self, other: 'TypeNode') -> bool:
        pass

    def is_arithmetic(self) -> bool:
        return False

    def is_three_way_comparable(self) -> bool:
        return False


class PrimitiveTypeNode(TypeNode, ABC):
    def __str__(self) -> str:
        return self.kind

    def is_equivalent(self, other: 'TypeNode') -> bool:
        return isinstance(other, PrimitiveTypeNode) and self.kind == other.kind


class NilTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Nil')

    def accept(self, visitor: 'AbstractVisitor') -> None:
        raise NotImplementedError()  # v0.0.3


class BoolTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Bool')

    def accept(self, visitor: 'AbstractVisitor') -> None:
        raise NotImplementedError()  # v0.0.3


class RealTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Real')

    def accept(self, visitor: 'AbstractVisitor') -> None:
        raise NotImplementedError()  # v0.0.3

    def is_arithmetic(self) -> bool:
        return True

    def is_three_way_comparable(self) -> bool:
        return True


class StringTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('String')

    def accept(self, visitor: 'AbstractVisitor') -> None:
        raise NotImplementedError()  # v0.0.3

    def is_three_way_comparable(self) -> bool:
        return True
