from typing import List, Literal


DiagnosticKind = Literal['info', 'warning', 'error']


class Diagnostic:
    def __init__(self, kind: DiagnosticKind, message: str, position: int):
        self.kind = kind
        self.message = message
        self.position = position

    def __str__(self):
        color = self.color_table.get(self.kind, '\033[1;94m')
        color_reset = '\033[0m'
        return f'{color}{self.kind}{color_reset}: {self.message}'

    color_table = {
        'info': '\033[1;94m',  # general information, for verbose
        'warning': '\033[1;93m',  # compiler warnings, such as unused variables
        'error': '\033[1;91m',  # compiler errors, such as syntax errors or type errors
    }


class Diagnostics:
    def __init__(self, verbose: bool) -> None:
        self.__diagnostics: List[Diagnostic] = []
        self.__last_block = 0
        self.__has_error = False
        self.__verbose = verbose

    def __iter__(self):
        return iter(self.__diagnostics)

    def __len__(self):
        return len(self.__diagnostics)

    def has_error(self):
        return self.__has_error

    def emit_diagnostic(self, kind: DiagnosticKind, message: str, position: int):
        if kind == 'info' and not self.__verbose:
            return
        elif kind == 'error':
            self.__has_error = True
        self.__diagnostics.append(Diagnostic(kind, message, position))

    def next_set(self):
        # sort diagnostics in current set by position
        idx = len(self.__diagnostics)
        self.__diagnostics[self.__last_block:idx] = sorted(
            self.__diagnostics[self.__last_block:idx], key=lambda diagnostic: diagnostic.position)
        self.__last_block = idx
