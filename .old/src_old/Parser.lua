--- @class Parser
--- @field _compiler Compiler
local Parser = {}
Parser.__index = Parser

--- @param compiler Compiler
--- @return Parser parser
function Parser.new(compiler)
	return setmetatable({
		_compiler = compiler,
	}, Parser)
end

function Parser:getCompiler()
	return self._compiler
end

function Parser:parse()
	error("not yet implemented")
end

return Parser
