--- @class Token
--- @field kind TokenKind
--- @field value TokenValue
local Token = {}

--- @alias TokenKind EofTokenKind | CtaTokenKind | LiteralTokenKind | NameTokenKind | TypeNameTokenKind | KeywordTokenKind | PunctuationTokenKind
--- @alias TokenValue nil | boolean | number | string
--- @alias EofTokenKind "" end of file
--- @alias CtaTokenKind "#@" compiler test assertion
--- @alias LiteralTokenKind "nil" | "true" | "false" | "<real>" | "<string>"
--- @alias NameTokenKind "<identifier>"
--- @alias TypeNameTokenKind "Nil" | "Bool" | "Real" | "String"
--- @alias KeywordTokenKind "def"
--- @alias PunctuationTokenKind "(" | ")" | "{" | "}" | "," | "=" | "!" | "+" | "-" | "*" | "/" | "%" | "<" | ">" | "==" | "!=" | "<=" | ">=" | "||" | "&&"

--- @param kind TokenKind
--- @param value TokenValue
--- @return Token token
function Token.new(kind, value)
	return {
		kind = kind,
		value = value,
	}
end

return Token
