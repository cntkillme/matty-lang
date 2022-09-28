local Compiler = require("Compiler")

local source = [[
	# literal tokens
		nil true false
		1. .1 1.1 11
		'' "" 'ab"c' "ab'c"
	# name tokens
		a _a1 $ $0 $f
	# type name tokens
		Nil Bool Real String
	# keyword tokens
		def if elseif else while break continue pass return
	# punctuation tokens
		( ) { } , : = ! + - * / % < > == != <= >= || && ->
	# malformed tokens
		. 1.. 1.0.
		123a $$123 abc$
		@
		"unterminated]]

	-- stylua: ignore
	local expectedResult = {
		"nil",
		"true", "false",
		{ "<real>", 1 }, { "<real>", 0.1 }, { "<real>", 1.1 }, { "<real>", 11 },
		{ "<string>", "" }, { "<string>", "" }, { "<string>", 'ab"c' }, { "<string>", "ab'c" },
		{ "<identifier>", "a" }, { "<identifier>", "_a1" }, { "<intrinsic>", "" }, { "<intrinsic>", "0" }, { "<intrinsic>", "f" },
		"Nil", "Bool", "Real", "String",
		"def", "if", "elseif", "else", "while", "break", "continue", "pass", "return",
		"(",  ")",  "{",  "}",  ",",  ":", "=", "!",  "+",  "-",  "*",  "/",  "%",  "<",  ">",  "==", "!=", "<=", ">=", "||", "&&", "->",
		{ "<real>", 0 }, { "<real>", 0 }, { "<real>", 0 },
		{ "<real>", 123 }, { "<identifier>", "a" }, { "<intrinsic>", "" }, { "<intrinsic>", "123" }, { "<identifier>", "abc" }, { "<intrinsic>", "" },
		{ "<string>", "unterminated" },
	}
local expectedDiagnostics = {
	{ "error", 'malformed real literal "."', 14, 3 },
	{ "error", 'malformed real literal "1.."', 14, 5 },
	{ "error", 'malformed real literal "1.0."', 14, 9 },
	{ "warning", 'consider adding a space after "123"', 15, 3 },
	{ "warning", 'consider adding a space after "$"', 15, 8 },
	{ "warning", 'consider adding a space after "abc"', 15, 14 },
	{ "error", 'unexpected character "@"', 16, 3 },
	{ "error", "unterminated string", 17, 3 },
}

local compiler = Compiler.new({ file = "<inline>", source = source })
local lexer = compiler:getLexer()
assert(lexer:getCompiler() == compiler)

-- get result
local result = {}
local kind, value = lexer:getToken()
assert(lexer:getToken() == kind)
while kind do
	table.insert(result, { kind, value })
	kind, value = lexer:nextToken()
end

-- compare result
for idx = 1, math.max(#result, #expectedResult) do
	local got = result[idx]
	local expected = expectedResult[idx]
	assert(got and expected)
	if type(expected) == "string" then
		assert(got[1] == expected)
	else
		assert(got[1] == expected[1])
		assert(got[2] == expected[2])
	end
end

-- compare diagnostics
local diagnostics = compiler:getDiagnostics()
for idx = 1, math.max(#diagnostics, #expectedDiagnostics) do
	local got = diagnostics[idx]
	local expected = expectedDiagnostics[idx]
	assert(got and expected)
	assert(got.kind == expected[1])
	assert(got.message == expected[2])
	assert(got.line == expected[3])
	assert(got.column == expected[4])
end
