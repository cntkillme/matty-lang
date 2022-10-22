from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar


if TYPE_CHECKING:
    from mattylang.lexer import Token
    from mattylang.visitor import AbstractVisitor


class AbstractNode(ABC):
    @abstractmethod
    def __init__(self, kind: str):
        self.__kind = kind
        self.parent: Optional['AbstractNode'] = None
        self.token = None  # first token
        self.invalid = False

    def __str__(self):
        return self.kind

    @abstractmethod
    def accept(self, visitor: 'AbstractVisitor') -> None:
        pass

    @property
    def kind(self) -> str:
        return self.__kind

    def add_token(self, token: 'Token'):
        self.token = token
        return self

    def copy_context(self, node: 'AbstractNode'):
        self.token = node.token
        self.invalid = node.invalid
        return self

    def get_location(self):
        if self.token is not None:
            return self.token.line, self.token.column
        else:
            return 0, 0


T = TypeVar('T', bound=AbstractNode)


class NodeList(Generic[T]):
    def __init__(self, parent: AbstractNode):
        self.parent = parent
        self.nodes: List[T] = []

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def get_parent(self):
        return self.parent

    def add_node(self, node: T):
        node.parent = self.parent
        self.nodes.append(node)
