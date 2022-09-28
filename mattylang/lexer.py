from string import ascii_letters, digits, punctuation, whitespace
from typing import Callable, Tuple

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
        elif self.kind == 'int_literal':
            return f'int_literal({self.lexeme})'
        elif self.kind == 'real_literal':
            return f'real_literal({self.lexeme})'
        elif self.kind == 'string_literal':
            return f'string_literal({repr(self.lexeme)})'
        else:
            return self.kind


class Lexer:
    def __init__(self, module: Module):
        self.__module = module
        self.__source = module.get_source()
        self.__position = 0
        self.__line = 1
        self.__column = 1
        self.__token = Token('eof', '', self.__position, self.__line, self.__column)

    def get_module(self) -> Module:
        return self.__module

    def get_position(self) -> int:
        return self.__position

    def get_location(self) -> Tuple[int, int]:
        return self.__line, self.__column

    def get_token(self) -> Token:
        return self.__token

    def scan(self) -> Token:
        self.__token = self.__scan_impl()
        self.__module.get_diagnostics().emit_info(f'scanned {self.__token}', self.__token.line, self.__token.column)
        return self.__token

    __space_set = set(whitespace)
    __digit_set = set(digits)
    __id_init_set = set(ascii_letters + '$_')
    __string_char_set = set(ascii_letters + digits + punctuation + ' \t')
    __keyword_set = {'def', 'nil', 'true', 'false'}
    __punctuation = {'(', ')', '{', '}', '=', '!', '+', '-', '*', '/',
                     '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&'}

    def __scan_impl(self) -> Token:
        chr = self.__get_char()
        diagnostics = self.__module.get_diagnostics()
        position, line, column = self.__position, self.__line, self.__column

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
        elif chr in self.__digit_set or chr == '.':  # int/real literal
            lexeme = self.__collect_lexeme(lambda chr: chr in self.__digit_set)
            kind = 'real_literal' if self.__get_char() == '.' else 'int_literal'

            if kind == 'real_literal':
                self.__next_char()
                lexeme = lexeme + '.' + self.__collect_lexeme(lambda chr: chr in self.__digit_set)

            if lexeme == '.':
                diagnostics.emit_error(f"expected digit near '.'", line, column)
                lexeme = '0.0'

            chr = self.__get_char()
            if chr in self.__id_init_set or chr == '.':
                diagnostics.emit_warning(f'expected whitespace after numeric literal {lexeme}', *self.get_location())

            return Token(kind, lexeme, position, line, column)
        elif chr == '"' or chr == "'":  # string literal
            quote = chr
            self.__next_char()
            text = self.__collect_lexeme(lambda chr: chr != quote and chr in self.__string_char_set)
            if self.__get_char() != quote:
                quote_str = "double quote" if quote == '"' else "single quote"
                diagnostics.emit_error(f'expected {quote_str} to terminate string', *self.get_location())
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
        return self.__source[self.__position] if self.__position < len(self.__source) else ''

    def __next_char(self):
        if self.__position < len(self.__source):
            chr = self.__get_char()
            self.__position += 1

            if chr == '\n':
                self.__line += 1
                self.__column = 1
            else:
                self.__column += 1

        return self.__get_char()

    def __next_char_while(self, predicate: Callable[[str], bool]):
        while self.__position < len(self.__source) and predicate(self.__get_char()):
            self.__next_char()
        return chr

    def __collect_lexeme(self, predicate: Callable[[str], bool]):
        start = self.__position
        self.__next_char_while(predicate)
        return self.__source[start:self.__position]
