from math import pi

from mattylang.ast.expression import IdentifierNode, RealLiteralNode
from mattylang.ast.statement import VariableDefinitionNode
from mattylang.symbols import Scope

globals = Scope()
globals.register('pi', VariableDefinitionNode(IdentifierNode('pi'), RealLiteralNode(pi)))
