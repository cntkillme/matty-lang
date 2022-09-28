local Reader = require("Reader")
local Lexer = require("Lexer")
local Parser = require("Parser")

--- @class Compiler
--- @field _options CompilerOptions
--- @field _diagnostics Diagnostic[]
--- @field _context integer[][] reader context stack
--- @field _reader Reader
--- @field _lexer Lexer
--- @field _parser Parser
local Compiler = {}
Compiler.__index = Compiler

--- @class CompilerOptions
--- @field file string
--- @field source string?

--- @class Diagnostic
--- @field kind DiagnosticKind
--- @field message string
--- @field line integer
--- @field column integer

--- @alias DiagnosticKind "note" | "warning" | "error"

--- @param options CompilerOptions
--- @return Compiler compiler
function Compiler.new(options)
	local self = setmetatable({}, Compiler)
	self._options = options
	self._diagnostics = {}
	self._context = {}
	self._reader = Reader.new(self)
	self._lexer = Lexer.new(self)
	self._parser = Parser.new(self)
	return self
end

function Compiler:getOptions()
	return self._options
end

function Compiler:getDiagnostics()
	return self._diagnostics
end

function Compiler:getReader()
	return self._reader
end

function Compiler:getLexer()
	return self._lexer
end

function Compiler:getParser()
	return self._parser
end

function Compiler:compile()
	error("not yet implemented")
end

--- Pushes the current reader context onto the reader context stack.
--- @return integer position
--- @return integer line
--- @return integer column
function Compiler:pushContext()
	local position, line, column = self._reader:getContext()
	table.insert(self._context, { position, line, column })
	return position, line, column
end

--- Pops the most-recently-pushed reader context from the reader context stack.
--- @return integer position
--- @return integer line
--- @return integer column
function Compiler:popContext()
	assert(#self._context > 0, "fatal: Compiler:popContext(): no context")
	local context = table.remove(self._context)
	return context[1], context[2], context[3]
end

--- Returns the most-recently-pushed reader context from the reader context stack.
--- If the stack is empty, returns the current reader's context.
--- @return integer position
--- @return integer line
--- @return integer column
function Compiler:peekContext()
	if #self._context > 0 then
		local context = self._context[#self._context]
		return context[1], context[2], context[3]
	else
		return self._reader:getContext()
	end
end

--- @param kind DiagnosticKind
--- @param message string
function Compiler:addDiagnostic(kind, message)
	local _, line, column = self:peekContext()
	table.insert(self._diagnostics, {
		kind = kind,
		message = message,
		line = line,
		column = column,
	})
end

return Compiler
