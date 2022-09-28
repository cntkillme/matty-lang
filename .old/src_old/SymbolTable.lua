--- @class SymbolTable
--- @field _compiler Compiler
--- @field _parent SymbolTable?
--- @field _nodes {[string]: Node }
local SymbolTable = {}
SymbolTable.__index = SymbolTable

--- @param compiler Compiler
function SymbolTable.new(compiler)
	return setmetatable({
		_compiler = compiler,
		_parent = nil,
		_nodes = {},
	}, SymbolTable)
end

--- @param name string
function SymbolTable:lookup(name, )

end

return SymbolTable
