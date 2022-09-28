from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from compiler.scope import Symbol, Scope


class AbstractNode(ABC):
    @abstractmethod
    def __init__(self, kind: str):
        self.__kind = kind
        self.__parent: Optional[AbstractNode] = None

    def get_kind(self):
        return self.__kind

    def get_parent(self):
        return self.__parent

    def set_parent(self, parent: 'AbstractNode'):
        self.__parent = parent


class ProgramNode(AbstractNode):
    def __init__(self, chunk: 'ChunkNode'):
        super().__init__('program')
        chunk.set_parent(self)
        self.__chunk = chunk

    def get_chunk(self):
        return self.__chunk


class StatementNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)


class ChunkNode(StatementNode):
    def __init__(self, statements: List['StatementNode']):
        super().__init__('chunk')
        for statement in statements:
            statement.set_parent(self)
        self.__statements = statements
        self.__scope: Optional['Scope'] = None

    def get_statements(self):
        return self.__statements

    def get_scope(self):
        return self.__scope

    def set_scope(self, symbols: 'Scope'):
        self.__scope = symbols


class VariableDefinitionNode(StatementNode):
    def __init__(self, name: 'IdentifierNode', value: 'ExpressionNode'):
        super().__init__('variable_definition')
        name.set_parent(self)
        self.__name = name
        value.set_parent(self)
        self.__value = value

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.__value


class VariableAssignmentNode(StatementNode):
    def __init__(self, name: 'IdentifierNode', value: 'ExpressionNode'):
        super().__init__('variable_assignment')
        name.set_parent(self)
        self.__name = name
        value.set_parent(self)
        self.__value = value

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.__value


class ExpressionNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str, type: Optional['TypeNode'] = None):
        super().__init__(kind)
        self.__type = type

    def get_type(self):
        return self.__type

    def set_type(self, type: 'TypeNode'):
        self.__type = type


class PrimaryExpressionNode(ExpressionNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)


class UnaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode):
        super().__init__('unary_expression')
        self.__operator = operator
        operand.set_parent(self)
        self.__operand = operand

    def get_operator(self):
        return self.__operator

    def get_operand(self):
        return self.__operand


class BinaryExpressionNode(ExpressionNode):
    def __init__(self, operator: str, left: ExpressionNode, right: ExpressionNode):
        super().__init__('binary_expression')
        self.__operator = operator
        left.set_parent(self)
        self.__left = left
        right.set_parent(self)
        self.__right = right

    def get_operator(self):
        return self.__operator

    def get_left(self):
        return self.__left

    def get_right(self):
        return self.__right


class NilLiteralNode(PrimaryExpressionNode):
    def __init__(self):
        super().__init__('nil_literal')


class BoolLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: bool):
        super().__init__('bool_literal')
        self.__value = value

    def get_value(self):
        return self.__value


class RealLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: float):
        super().__init__('real_literal')
        self.__value = value

    def get_value(self):
        return self.__value


class StringLiteralNode(PrimaryExpressionNode):
    def __init__(self, value: str):
        super().__init__('string_literal')
        self.__value = value

    def get_value(self):
        return self.__value


class IdentifierNode(PrimaryExpressionNode):
    def __init__(self, text: str, symbol: Optional['Symbol'] = None):
        super().__init__('identifier')
        self.__text = text
        self.__symbol = symbol
        self.__forward_reference = False

    def get_text(self):
        return self.__text

    def get_symbol(self):
        return self.__symbol

    def set_symbol(self, symbol: 'Symbol'):
        self.__symbol = symbol

    def is_forward_reference(self):
        return self.__forward_reference

    def set_forward_reference(self, forward_reference: bool):
        self.__forward_reference = forward_reference


class TypeNode(AbstractNode, ABC):
    @abstractmethod
    def __init__(self, kind: str):
        super().__init__(kind)

    @abstractmethod
    def get_type_name(self) -> str:
        pass


class PrimitiveTypeNode(TypeNode, ABC):
    pass


class NilTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Nil')

    def get_type_name(self):
        return 'Nil'


class BoolTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Bool')

    def get_type_name(self):
        return 'Bool'


class RealTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('Real')

    def get_type_name(self):
        return 'Real'


class StringTypeNode(PrimitiveTypeNode):
    def __init__(self):
        super().__init__('String')

    def get_type_name(self):
        return 'String'
