from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mattylang.ast.core import AbstractNode

if TYPE_CHECKING:
    from mattylang.visitor import AbstractVisitor


class TypeNode(AbstractNode, ABC):
    @abstractmethod
    def is_equivalent(self, other: 'TypeNode') -> bool:
        pass

    def is_arithmetic(self) -> bool:
        return False

    def is_three_way_comparable(self) -> bool:
        return False


class PrimitiveTypeNode(TypeNode, ABC):
    def is_equivalent(self, other: 'TypeNode'):
        return isinstance(self, other.__class__)


class NilTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return 'Nil'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_nil_type(self)


class BoolTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return 'Bool'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_bool_type(self)


class RealTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return 'Real'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_real_type(self)

    def is_arithmetic(self) -> bool:
        return True

    def is_three_way_comparable(self) -> bool:
        return True


class StringTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        return 'String'

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_string_type(self)

    def is_three_way_comparable(self) -> bool:
        return True


class FunctionTypeNode(TypeNode, ABC):
    def __init__(self, return_type: TypeNode, parameters: list[TypeNode]):
        super().__init__()
        self.return_type = return_type
        self.parameter_types = parameters

    def __str__(self) -> str:
        return f'({self.parameter_types}) -> {self.return_type}'

    def is_equivalent(self, other: 'TypeNode') -> bool:
        if not isinstance(other, FunctionTypeNode):
            return False
        elif not self.return_type.is_equivalent(other.return_type):
            return False
        elif len(self.parameter_types) != len(other.parameter_types):
            return False

        for i in range(len(self.parameter_types)):
            if not self.parameter_types[i].is_equivalent(other.parameter_types[i]):
                return False

        return True

    def accept(self, visitor: 'AbstractVisitor') -> None:
        visitor.visit_function_type(self)
