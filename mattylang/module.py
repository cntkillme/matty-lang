from sys import stdout, stderr
from typing import Optional

from mattylang.diagnostics import Diagnostic, Diagnostics
from mattylang.linemap import LineMap
from mattylang.symbols import SymbolTable


class Module:
    def __init__(self, file: str, source: str, globals: Optional[SymbolTable] = None, verbose: bool = False):
        self.file = file
        self.source = source
        self.globals = globals if globals is not None else SymbolTable()
        self.verbose = verbose
        self.diagnostics = Diagnostics(verbose)
        self.line_map = LineMap(source)

    def reset(self):
        self.globals.reset()
        self.diagnostics = Diagnostics(self.verbose)

    def format_diagnostic(self, diagnostic: Diagnostic):
        line, column = self.line_map.get_location(diagnostic.position)
        return f'{self.file}:{line}:{column}: {diagnostic}'

    def print_diagnostic(self, diagnostic: Diagnostic):
        print(self.format_diagnostic(diagnostic), file=stdout if diagnostic.kind == 'info' else stderr)

    def print_diagnostics(self):
        for diagnostic in self.diagnostics:
            self.print_diagnostic(diagnostic)
