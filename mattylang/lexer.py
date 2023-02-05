from string import ascii_letters, digits, punctuation, whitespace
from typing import Callable, Optional

from mattylang.module import Module


class Token:
    def __init__(self, kind: str, lexeme: str, position: int) -> None:
        self.kind = kind
        self.lexeme = lexeme
        self.position = position

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
        self.__module = module
        self.__source = module.source
        self.__position = 0
        self.__token: Optional[Token] = None

    def get_module(self) -> Module:
        return self.__module

    def peek(self):
        if self.__token is None:
            return self.scan()
        return self.__token

    def scan(self):
        self.__token = self.__scan_impl()
        # self.__module.diagnostics.emit_diagnostic('info', f'syntax: scanned {self.__token}', self.__token.position)
        return self.__token

    __space_set = set(whitespace)
    __digit_set = set(digits)
    __id_init_set = set(ascii_letters + '$_')
    __string_char_set = set(ascii_letters + digits + punctuation + ' \t')
    __keyword_set = {'def', 'nil', 'true', 'false', 'if', 'else', 'while',
                     'break', 'continue', 'return', 'Nil', 'Bool', 'Real', 'String'}
    __punctuation = {'(', ')', '{', '}', '=', '!', '+', '-', '*', '/',
                     '%', '<', '>', '==', '!=', '<=', '>=', '||', '&&', '->'}

    def __scan_impl(self) -> Token:
        chr = self.__get_char()
        diagnostics = self.__module.diagnostics
        position = self.__position

        if chr == '':  # eof
            return Token('eof', '', position)
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
            return Token(kind, lexeme, position)
        elif chr in self.__digit_set or chr == '.':  # real literal
            lexeme = self.__collect_lexeme(lambda chr: chr in self.__digit_set)
            kind = 'real_literal'

            if self.__get_char() == '.':
                self.__next_char()
                lexeme = lexeme + '.' + self.__collect_lexeme(lambda chr: chr in self.__digit_set)

            if lexeme == '.':
                diagnostics.emit_diagnostic('error', f'syntax: unexpected character .', position)
                return self.__scan_impl()

            if self.__get_char() in self.__id_init_set or self.__get_char() == '.':
                diagnostics.emit_diagnostic(
                    'warning', f'syntax: expected whitespace after real literal {lexeme}', position)

            return Token('real_literal', lexeme, position)
        elif chr == '"' or chr == "'":  # string literal
            quote = chr
            self.__next_char()
            text = self.__collect_lexeme(lambda chr: chr != quote and chr in self.__string_char_set)

            if self.__get_char() != quote:
                diagnostics.emit_diagnostic(
                    'error', f'syntax: expected {quote} to terminate string', self.__position)
            else:
                self.__next_char()

            return Token('string_literal', text, position)
        else:  # punctuation/other
            # greedily matches longest valid punctuation
            op1 = chr
            op2 = op1 + self.__next_char()
            if len(op2) == 2 and op2 in self.__punctuation:
                self.__next_char()
                return Token(op2, op2, position)
            elif op1 in self.__punctuation:
                return Token(op1, op1, position)
            else:
                # continue if unexpected character
                diagnostics.emit_diagnostic('error', f'syntax: unexpected character {repr(op1)}', position)
                return self.__scan_impl()

    def __get_char(self):
        return self.__source[self.__position] if self.__position < len(self.__source) else ''

    def __next_char(self):
        if self.__position < len(self.__source):
            self.__position += 1
        return self.__get_char()

    def __next_char_while(self, predicate: Callable[[str], bool]):
        while self.__position < len(self.__source) and predicate(self.__get_char()):
            self.__next_char()
        return chr

    def __collect_lexeme(self, predicate: Callable[[str], bool]):
        start = self.__position
        self.__next_char_while(predicate)
        return self.__source[start:self.__position]
