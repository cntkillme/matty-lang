--- @class Reader
--- @field _compiler Compiler
--- @field _file string
--- @field _source string
--- @field _position integer
--- @field _line integer
--- @field _column integer
local Reader = {}
Reader.__index = Reader

--- @param compiler Compiler
--- @return Reader reader
function Reader.new(compiler)
	local options = compiler:getOptions()
	local file = options.file
	local source = options.source

	if not source then
		-- The source file is read in binary mode to ensure the cursor is consistent across platforms.
		-- Otherwise, platform-specific replacements (e.g., `\r\n` -> `\n` on Windows) will offset the cursor.
		local fd = assert(io.open(file, "rb"))
		source = fd:read("a")
		fd:close()
	end

	return setmetatable({
		_compiler = compiler,
		_file = file,
		_source = source,
		_position = 1,
		_line = 1,
		_column = 1,
	}, Reader)
end

function Reader:getCompiler()
	return self._compiler
end

function Reader:getFile()
	return self._file
end

function Reader:getSource()
	return self._source
end

function Reader:getPosition()
	return self._position
end

function Reader:getLocation()
	return self._line, self._column
end

--- Gets the current character, skips invalid characters.
function Reader:getChar()
	local chr = self._source:sub(self._position, self._position)
	while chr ~= "" and chr:find("[^%g%s]") do
		chr = self:_advanceChar()
	end
	return chr
end

--- Advances the reader to get the next character, skipping invalid characters.
function Reader:nextChar()
	self:_advanceChar()
	return self:getChar()
end

--- @param i integer lower-bound, inclusive
--- @param j integer upper-bound, exclusive
function Reader:querySource(i, j)
	-- wrapped in parenthesis to drop second return value of gsub
	return (self._source:sub(i, j - 1):gsub("[^%g%s]", ""))
end

--- Advances the reader while the character matches the specified Lua string pattern.
--- @param pattern string
function Reader:consumeChars(pattern)
	local chr = self:getChar()
	while chr ~= "" and chr:find(pattern) do
		chr = self:nextChar()
	end
	return chr
end

--- @param pattern string
--- @return string
function Reader:consumeAndQuery(pattern)
	local start = self:getPosition()
	self:consumeChars(pattern)
	return self:querySource(start, self:getPosition())
end

--- Processes the current character and advances the reader once.
function Reader:_advanceChar()
	local chr = self._source:sub(self._position, self._position)

	-- process character
	if chr ~= "" then
		-- emit diagnostic for invalid characters
		if chr:find("[^%g%s]") then
			self._compiler:addDiagnostic("error", ("invalid character %q"):format(chr))
		end

		-- update line and column on LF
		if chr == "\n" then
			self._line = self._line + 1
			self._column = 1
		else
			self._column = self._column + 1
		end

		-- advance the reader
		self._position = self._position + 1
	end

	return self._source:sub(self._position, self._position)
end

return Reader
