local Compiler = require("Compiler")

-- test implementation
do
	local source = "a\0\nb"
	local expectedResult = "a\nb"
	local expectedDiagnostics = { { "error", 'invalid character "\\0"', 1, 2 } }
	local compiler = Compiler.new({ file = "<inline>", source = source })
	local reader = compiler:getReader()
	assert(reader:getCompiler() == compiler)
	assert(reader:getFile() == compiler:getOptions().file)
	assert(reader:getSource() == compiler:getOptions().source)
	assert(reader:getPosition() == 1)
	local position, line, column = reader:getContext()
	assert(position == 1 and line == 1 and column == 1) -- after shebang
	assert(reader:getPosition() == position)
	assert(reader:querySource(1, #source + 1) == expectedResult)

	local read = ""
	local chr = reader:getChar()
	while chr ~= "" do
		read = read .. chr
		chr = reader:nextChar()
	end
	assert(read == expectedResult)
	assert(reader:getPosition() == #source + 1)

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

	-- hack: revert to test consumeChars
	reader._position, reader._line, reader._column = position, line, column
end

-- test reading from file
do
	local file = "./examples/v1features.mtl"
	local compiler = Compiler.new({ file = file })
	local reader = compiler:getReader()
	local fd = assert(io.open(file, "rb"))
	local source = fd:read("*a")
	fd:close()
	assert(reader:getSource() == source)
end
