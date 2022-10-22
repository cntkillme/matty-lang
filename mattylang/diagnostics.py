import sys
from typing import Iterator, List, Optional


class Diagnostic:
    def __init__(self, kind: str, message: str, line: int, column: int) -> None:
        self.kind = kind
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        color = '\033[1;91m' if self.kind == 'error' else '\033[1;93m' if self.kind == 'warning' else '\033[1;94m'
        return f'{color}{self.kind}\033[0m: {self.message}'

    def format(self, file: Optional[str]):
        if file:
            return f'{file}:{self.line}:{self.column}: {self}'
        else:
            return f'{self} at line {self.line}, column {self.column}'

    def print(self, file: Optional[str]):
        print(self.format(file), file=sys.stdout if self.kind == 'info' else sys.stderr)


class Diagnostics:
    def __init__(self, verbose: bool) -> None:
        self.__diagnostics: List[Diagnostic] = []
        self.__has_error = False
        self.__verbose = verbose

    def __iter__(self) -> Iterator[Diagnostic]:
        return iter(self.__diagnostics)

    def has_error(self) -> bool:
        return self.__has_error

    def emit_info(self, message: str, line: int, column: int) -> None:
        if self.__verbose:
            self.__emit_diagnostic(Diagnostic('info', message, line, column))

    def emit_warning(self, message: str, line: int, column: int) -> None:
        self.__emit_diagnostic(Diagnostic('warning', message, line, column))

    def emit_error(self, message: str, line: int, column: int) -> None:
        self.__emit_diagnostic(Diagnostic('error', message, line, column))

    def sort(self):
        self.__diagnostics.sort(key=lambda diagnostic: (diagnostic.line, diagnostic.column))

    def __emit_diagnostic(self, diagnostic: Diagnostic) -> None:
        self.__diagnostics.append(diagnostic)
        if diagnostic.kind == 'error' or diagnostic.kind == 'fatal':
            self.__has_error = True
