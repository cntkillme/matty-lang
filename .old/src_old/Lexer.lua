local Token = require("Token")

--- @class Lexer
--- @field _compiler Compiler
--- @field _token Token
local Lexer = {}
Lexer.__index = Lexer

Lexer.keywordSet = {
	["nil"] = true,
	["true"] = true,
	["false"] = true,
	["Nil"] = true,
	["Bool"] = true,
	["Real"] = true,
	["String"] = true,
	["def"] = true,
}

Lexer.punctuationSet = {
	["("] = true,
	[")"] = true,
	["{"] = true,
	["}"] = true,
	[","] = true,
	["="] = true,
	["!"] = true,
	["+"] = true,
	["-"] = true,
	["*"] = true,
	["/"] = true,
	["%"] = true,
	["<"] = true,
	[">"] = true,
	["=="] = true,
	["!="] = true,
	["<="] = true,
	[">="] = true,
	["||"] = true,
	["&&"] = true,
}

--- @param compiler Compiler
--- @return Lexer lexer
function Lexer.new(compiler)
	return setmetatable({
		_compiler = compiler,
		_token = Token.new("eof"),
	}, Lexer)
end

function Lexer:getCompiler()
	return self._compiler
end

function Lexer:getToken()
	if self._kind then
		return self._token
	else
		return self:nextToken()
	end
end

function Lexer:nextToken()
	local reader = self._compiler:getReader()
	local chr = reader:getChar()
	self._kind = nil -- eof
	self._value = nil
	if chr == "#" then -- comment
		-- skip line
		reader:consumeChars("[^\n]")
		reader:nextChar()
		return self:nextToken()
	elseif chr:find("%s") then -- whitespace
		reader:consumeChars("%s")
		return self:nextToken()
	elseif chr:find("[%a_$]") then -- names and keywords
		self._compiler:pushContext()
		self:_scanNamed()
		self._compiler:popContext()
	elseif chr:find("[%d%.]") then -- real literal
		self._compiler:pushContext()
		self:_scanRealLiteral()
		self._compiler:popContext()
	elseif chr == '"' or chr == "'" then -- string literal
		self._compiler:pushContext()
		self:_scanStringLiteral()
		self._compiler:popContext()
	elseif chr:find("%p") then -- punctuation
		self._compiler:pushContext()
		self:_scanPunctuation()
		self._compiler:popContext()
	end
	return self._token
end

--- Precondition: current character is a letter, underscore, or intrinsic specifier ("$").
function Lexer:_scanNamed()
	local reader = self._compiler:getReader()
	local intrinsic = reader:getChar() == "$"

	if intrinsic then
		-- skip intrinsic specifier
		reader:nextChar()
	end

	local lexeme = reader:consumeAndQuery("[%w_]")
	local chr = reader:getChar()

	if intrinsic then -- intrinsic
		self._kind = "<intrinsic>"
		self._value = lexeme
	elseif Lexer.keywordSet[lexeme] then -- keyword
		self._kind = lexeme
	else -- identifier
		self._kind = "<identifier>"
		self._value = lexeme
	end

	if chr == "$" then
		self._compiler:addDiagnostic(
			"warning",
			("consider adding a space after %q"):format(intrinsic and "$" .. lexeme or lexeme)
		)
	end
end

--- Precondition: current character is a digit or decimal point.
function Lexer:_scanRealLiteral()
	local reader = self._compiler:getReader()
	local lexeme = reader:consumeAndQuery("[%d%.]")
	local value = tonumber(lexeme)
	self._kind = "<real>"
	self._value = value

	-- ensure the real literal is valid
	if not value then
		self._compiler:addDiagnostic("error", ("malformed real literal %q"):format(lexeme))
		self._value = 0
	end

	-- warn for "weird" token sequence (e.g., 2x, 2.x, 2$)
	local chr = reader:getChar()
	if chr ~= "" and chr:find("[%w$]") then
		self._compiler:addDiagnostic("warning", ("consider adding a space after %q"):format(lexeme))
	end
end

--- Precondition: current character is a quote.
function Lexer:_scanStringLiteral()
	local reader = self._compiler:getReader()
	local quote = reader:getChar()

	-- consume quote
	reader:nextChar()

	-- consume non-quote
	local lexeme = reader:consumeAndQuery("[^" .. quote .. "]")
	self._kind = "<string>"
	self._value = lexeme

	-- expect quote
	if reader:getChar() == quote then
		reader:nextChar()
	else
		self._compiler:addDiagnostic("error", "unterminated string")
	end
end

--- Precondition: current character is punctuation.
function Lexer:_scanPunctuation()
	local reader = self._compiler:getReader()
	local chr = reader:getChar()

	-- greedily match operators
	local op2 = chr .. reader:nextChar()
	if #op2 == 2 and Lexer.punctuationSet[op2] then
		-- match operators of length 2 first
		reader:nextChar()
		self._kind = op2
	elseif Lexer.punctuationSet[chr] then
		-- match operators of length 1 next
		self._kind = chr
	else
		-- unexpected character, recover by scanning the next token
		self._compiler:addDiagnostic("error", ("unexpected character %q"):format(chr))
		return self:nextToken()
	end
end

return Lexer
