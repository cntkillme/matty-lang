from string import ascii_letters, digits, punctuation, whitespace
from typing import Callable

from mattylang.module import Module


class Token:
    def __init__(self, kind: str, lexeme: str, position: int, line: int, column: int) -> None:
        self.kind = kind
        self.lexeme = lexeme
        self.position = position
        self.line = line
        self.column = column

    def __str__(self) -> str:
        if self.kind == 'identifier':
            return f'identifier({self.lexeme})'
        elif self.kind == 'real_literal':
            return f'real_literal({self.lexeme})'
        elif self.kind == 'string_literal':
            return f'string_literal({repr(self.lexeme)})'
        else:
            return self.kind


class Lexer:
    def __init__(self, module: Module):
        self.module = module
        self.source = module.source
        self.position = 0
        self.line = 1
        self.column = 1
        self.token = Token('eof', '', self.position, self.line, self.column)
        self.scan()

    def scan(self):
        self.token = self.__scan_impl()
        self.module.diagnostics.emit_info(f'scanned {self.token}', self.token.line, self.token.column)
        return self.token

    __space_set = set(whitespace)
    __digit_set = set(digits)
    __id_init_set = set(ascii_letters + '$_')
    __string_char_set = set(ascii_letters + digits + punctuation + ' \t')
    __keyword_set = {'def', 'nil', 'true', 'false'}
    __punctuation = {'(', ')', '{', '}', '=', '!', '+', '-', '*', '/',
                     '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&'}

    def __scan_impl(self) -> Token:
        chr = self.__get_char()
        diagnostics = self.module.diagnostics
        position, line, column = self.position, self.line, self.column

        if chr == '':  # eof
            return Token('eof', '', position, line, column)
        elif chr in self.__space_set:  # whitespace
            # skip whitespace and continue
            self.__next_char_while(lambda chr: chr in self.__space_set)
            return self.__scan_impl()
        elif chr == '#':  # comment
            # skip comment and continue
            self.__next_char_while(lambda chr: chr != '\n')
            self.__next_char()
            return self.__scan_impl()
        elif chr in self.__id_init_set:  # keyword/identifier
            lexeme = self.__collect_lexeme(lambda chr: chr in self.__id_init_set or chr in self.__digit_set)
            kind = lexeme if lexeme in self.__keyword_set else 'identifier'
            return Token(kind, lexeme, position, line, column)
        elif chr in self.__digit_set or chr == '.':  # real literal
            lexeme = self.__collect_lexeme(lambda chr: chr in self.__digit_set)
            kind = 'real_literal'

            if self.__get_char() == '.':
                self.__next_char()
                lexeme = lexeme + '.' + self.__collect_lexeme(lambda chr: chr in self.__digit_set)

            if lexeme == '.':
                diagnostics.emit_error(f'expected digit near .', line, column)
                lexeme = '0'

            if self.__get_char() in self.__id_init_set or self.__get_char() == '.':
                diagnostics.emit_warning(f'expected whitespace after real literal {lexeme}', self.line, self.column)

            return Token('real_literal', lexeme, position, line, column)
        elif chr == '"' or chr == "'":  # string literal
            quote = chr
            self.__next_char()
            text = self.__collect_lexeme(lambda chr: chr != quote and chr in self.__string_char_set)
            if self.__get_char() != quote:
                quote_str = 'double quote' if quote == '"' else 'single quote'
                diagnostics.emit_error(f'expected {quote_str} to terminate string', self.line, self.column)
            else:
                self.__next_char()
            return Token('string_literal', text, position, line, column)
        else:  # punctuation/other
            # greedily matches longest valid punctuation
            op1 = chr
            op2 = op1 + self.__next_char()
            if len(op2) == 2 and op2 in self.__punctuation:
                self.__next_char()
                return Token(op2, op2, position, line, column)
            elif op1 in self.__punctuation:
                return Token(op1, op1, position, line, column)
            else:
                # continue if unexpected character
                diagnostics.emit_error(f'unexpected character {repr(op1)}', line, column)
                return self.__scan_impl()

    def __get_char(self):
        return self.source[self.position] if self.position < len(self.source) else ''

    def __next_char(self):
        if self.position < len(self.source):
            chr = self.__get_char()
            self.position += 1

            if chr == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1

        return self.__get_char()

    def __next_char_while(self, predicate: Callable[[str], bool]):
        while self.position < len(self.source) and predicate(self.__get_char()):
            self.__next_char()
        return chr

    def __collect_lexeme(self, predicate: Callable[[str], bool]):
        start = self.position
        self.__next_char_while(predicate)
        return self.source[start:self.position]
