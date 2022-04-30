#!/usr/bin/lua
package.path = "./src/?.lua;" .. package.path

local Compiler = require("Compiler")
local StringUtil = require("util.StringUtil")

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
  matty source [file]    prints the source (invalid characters removed)
  matty tokens [file]    prints the tokens
  matty ast [file]       prints the abstract syntax tree

Notes:
  If a file is unspecified, standard input will be used.
  The shortcut 'CTRL + D' or 'CTRL + Z' can be used to terminate standard input.]])
end

--- @param file string
function commands.run(file)
	error("not yet implemented")
end

function commands.test()
	dofile("test/init.lua")
end

function commands.print(component, file)
	if not component then
		error("expected compiler component")
	end

	local source = nil

	if not file then
		file = "<stdin>"
		source = io.read("*a")
	end

	local compiler = Compiler.new({ file = file, source = source })

	if component == "reader" then
		local reader = compiler:getReader()
		local chr = reader:getChar()
		local chars = {}
		while chr ~= "" do
			table.insert(chars, chr)
			chr = reader:nextChar()
		end
		print(table.concat(chars))
	elseif component == "lexer" then
		local lexer = compiler:getLexer()
		local kind, value = lexer:getToken()
		local tokens = {}
		while kind ~= "" do
			if kind == "<real>" then
				-- invalid token produced for: infinities, NaNs, and values formatted in exponent notation
				-- precision may be lost as well
				table.insert(tokens, ("%g"):format(value))
			elseif kind == "<string>" then
				table.insert(tokens, '"' .. StringUtil.escape(value) .. '"')
			elseif kind == "<identifier>" then
				table.insert(tokens, value)
			elseif kind == "<intrinsic>" then
				table.insert(tokens, "$" .. value)
			else
				table.insert(tokens, kind)
			end
			kind, value = lexer:nextToken()
		end
		print(table.concat(tokens, " "))
	elseif component == "parser" then
		error("not yet implemented")
	else
		error("expected component: reader, lexer, or parser")
	end

	-- print diagnostics to stderr, colored with ANSI escape sequences
	local prefix = {
		note = "\x1B[01;36mnote\x1B[0m",
		warning = "\x1B[01;35mwarning\x1B[0m",
		error = "\x1B[01;31merror\x1B[0m",
	}

	for _, diagnostic in ipairs(compiler:getDiagnostics()) do
		io.stderr:write(
			("%s:%d:%d: %s: %s\n"):format(
				file,
				diagnostic.line,
				diagnostic.column,
				prefix[diagnostic.kind] or diagnostic.kind,
				diagnostic.message
			)
		)
	end
end

main(...)
