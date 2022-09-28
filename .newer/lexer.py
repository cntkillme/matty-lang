from string import ascii_letters, digits, punctuation, whitespace
from typing import Callable, Tuple

Token = Tuple[str, str]


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.token = self.__scan_impl()

    def scan(self):
        self.token = self.__scan_impl()
        return self.token

    __alnum_set = set(ascii_letters + digits)
    __alpha_set = set(ascii_letters)
    __digit_set = set(digits)
    __punct_set = set(punctuation)
    __space_set = set(whitespace)

    def __scan_impl(self) -> Token:
        chr = self.__get_char()
        if chr == '':  # eof
            return ('eof', '')
        elif chr in self.__space_set:  # whitespace
            self.__next_char_while(lambda chr: chr in self.__space_set)
            return self.__scan_impl()
        elif chr == '#':  # comment
            self.__next_char_while(lambda c: c != '\n')
            self.__next_char()
            return self.__scan_impl()
        elif chr in self.__alpha_set or chr == '$' or chr == '_':  # keyword/identifier
            token = self.__scan_text()
            return token
        elif chr in self.__digit_set or chr == '.':  # real literal
            return self.__scan_real_literal()
        elif chr == '"' or chr == "'":  # string literal
            return self.__scan_string_literal()
        elif chr in self.__punct_set:  # punctuation
            return self.__scan_punctuation()
        else:
            raise ValueError('unexpected character', chr)

    def __get_char(self):
        return self.source[self.position] if self.position < len(self.source) else ''

    def __next_char(self):
        if self.position < len(self.source):
            chr = self.__get_char()
            if chr == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
        return self.__get_char()

    def __next_char_while(self, predicate: Callable[[str], bool]):
        while self.position < len(self.source) and predicate(self.__get_char()):
            self.__next_char()
        return chr

    __keywords = {
        'def': True,
        'nil': True,
        'true': True,
        'false': True,
    }

    def __scan_text(self):
        start = self.position
        self.__next_char_while(
            lambda chr: chr in self.__alnum_set or chr == '$' or chr == '_')
        name = self.source[start:self.position]
        if name in self.__keywords:
            return (name, name)
        else:
            return ('<identifier>', name)

    def __scan_real_literal(self):
        start = self.position
        self.__next_char_while(lambda chr: chr in self.__digit_set)
        if self.__get_char() == '.':
            self.__next_char()
            self.__next_char_while(lambda chr: chr in self.__digit_set)
        lexeme = self.source[start:self.position]
        if lexeme == '.':
            raise ValueError('invalid real literal', lexeme)
        return ('<real>', self.source[start:self.position])

    def __scan_string_literal(self):
        start = self.position
        quote = self.__get_char()
        self.__next_char()
        self.__next_char_while(lambda chr: chr != quote)
        if self.__get_char() != quote:
            raise ValueError('expected character', quote)
        self.__next_char()
        return ('<string>', self.source[start + 1:self.position - 1])

    __punctuation = {
        '(': True, ')': True,
        '{': True, '}': True,
        ',': True,
        '=': True,
        '!': True,
        '+': True, '-': True, '*': True, '/': True, '%': True,
        '<': True, '>': True, '==': True, '!=': True, '<=': True, '>=': True,
        '||': True, '&&': True,
    }

    def __scan_punctuation(self):
        op1 = self.__get_char()
        op2 = op1 + self.__next_char()
        if op1 != op2 and op2 in self.__punctuation:
            self.__next_char()
            return (op2, op2)
        elif op1 in self.__punctuation:
            return (op1, op1)
        else:
            raise ValueError('unexpected character', op1)
