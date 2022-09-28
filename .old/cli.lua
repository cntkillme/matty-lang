#!/usr/bin/lua
package.path = "./src/?.lua;" .. package.path

local Compiler = require("Compiler")

local commands = {}

local function main(command, ...)
	if not command then
		commands.help()
		return
	end

	local handler = commands[command]

	if handler then
		handler(...)
	else
		error("unknown command")
	end
end

function commands.help()
	print([[
Usage:
  matty help             displays this message
  matty test             run the test suite
  matty run [file]       interpret a matty source file
  matty tokens [file]    prints the tokens
  matty tree [file]      prints the abstract syntax tree

Notes:
  If a file is unspecified, standard input will be used.
  The shortcut CTRL + D or CTRL + Z can be used to terminate standard input.]])
end

--- @param file string?
local function createCompiler(file)
	local source = nil --- @type string?
	if not file or file == "" then
		file = "<stdin>"
		source = io.read("*a")
	end
	return Compiler.new({ file = file, source = source })
end

--- @param file file*
--- @param compiler Compiler
local function emitDiagnostics(file, compiler)
	for _, diagnostic in ipairs(compiler:getDiagnostics()) do
		file:write(
			("%s:%d:%d: %s: %s\n"):format(
				compiler:getOptions().file,
				diagnostic.line,
				diagnostic.column,
				diagnostic.kind,
				diagnostic.message
			)
		)
	end
end

function commands.test()
	dofile("test/init.lua")
end

--- @param file string
function commands.run(file)
	error("not yet implemented")
end

--- @param file string?
function commands.source(file)
	local compiler = createCompiler(file)
	local reader = compiler:getReader()
	local chr = reader:getChar()
	local chars = {}
	while chr ~= "" do
		table.insert(chars, chr)
		chr = reader:nextChar()
	end
	print(table.concat(chars))
	emitDiagnostics(io.stderr, compiler)
end

--- @param file string?
function commands.tokens(file)
	local compiler = createCompiler(file)
	local lexer = compiler:getLexer()
	local tokens = {}
	local kind, value = lexer:getToken()
	while kind do
		if value ~= nil then
			table.insert(tokens, ("%s (%s)"):format(kind, tostring(value)))
		else
			table.insert(tokens, kind)
		end
		kind, value = lexer:nextToken()
	end
	print(table.concat(tokens, "\n"))
	emitDiagnostics(io.stderr, compiler)
end

main(...)
