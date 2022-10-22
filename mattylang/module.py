from mattylang.diagnostics import Diagnostics
from mattylang.globals import globals
from mattylang.symbols import Scope


class Module:
    def __init__(self, file: str, source: str, verbose: bool = False, globals: Scope = globals) -> None:
        self.file = file
        self.source = source
        self.diagnostics = Diagnostics(verbose)
        self.globals = globals

    def print_diagnostics(self) -> None:
        self.diagnostics.sort()
        for diagnostic in self.diagnostics:
            diagnostic.print(self.file)
