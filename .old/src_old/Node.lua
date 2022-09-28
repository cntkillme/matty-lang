--- @class Node
--- @field _kind NodeKind
--- @field _parent Node
--- @field _position number
--- @field _line number
--- @field _column number
local Node = {}
Node.__index = Node

--- @alias NodeKind ProgramNode | StatementNode | ExpressionNode | TypeNode
--- @alias ExpressionNode LiteralNode | QualifiedNameNode | UnaryExpressionNode | BinaryExpressionNode
--- @alias LiteralNode NilLiteralNode | BoolLiteralNode | RealLiteralNode | StringLiteralNode
--- @alias QualifiedNameNode IdentifierNode

--- @class ProgramNode : Node
--- @field body BlockNode

--- @class StatementNode : Node

--- @class BlockNode : StatementNode
--- @field statements StatementNode[]

--- @class VariableDefinitionNode : StatementNode
--- @field name IdentifierNode
--- @field value ExpressionNode

--- @class VariableAssignmentNode : StatementNode
--- @field name IdentifierNode
--- @field value ExpressionNode

--- @class ExpressionNode : Node
--- @field type TypeNode

--- @class TypeNode : Node
