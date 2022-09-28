from mattylang.lexer import Lexer


class TokenIterator:
    def __init__(self, lexer: Lexer):
        self.__lexer = lexer

    def __iter__(self):
        return self

    def __next__(self):
        token = self.__lexer.scan()
        if token.kind == 'eof':
            raise StopIteration
        else:
            return token
