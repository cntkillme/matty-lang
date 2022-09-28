package.path = "./src/?.lua;" .. package.path

local tests = {
	"test/compiler/Reader.test.lua",
	"test/compiler/Lexer.test.lua",
}


for _, path in ipairs(tests) do
	print(("test %q"):format(path))
	dofile(path)
end

print("all tests passed")
