from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional


if TYPE_CHECKING:
    from mattylang.ast.type import TypeNode
    from mattylang.visitor import AbstractVisitor


class AbstractNode(ABC):
    @abstractmethod
    def __init__(self, position: int = 0):
        self.parent: Optional[AbstractNode] = None
        self.position = position
        self.invalid = False  # if any errors are associated with this node or any child node

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


class Declaration(ABC):
    @abstractmethod
    def get_declared_name(self) -> str:
        pass

    @abstractmethod
    def get_declared_type(self) -> 'TypeNode':
        pass
