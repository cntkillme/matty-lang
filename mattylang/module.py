from sys import stdout, stderr

from mattylang.diagnostics import Diagnostic, Diagnostics
from mattylang.globals import globals
from mattylang.symbols import SymbolTable
from mattylang.linemap import LineMap


class Module:
    def __init__(self, file: str, source: str, verbose: bool = False, globals: SymbolTable = globals):
        self.file = file
        self.source = source
        self.diagnostics = Diagnostics(verbose)
        self.globals = globals
        self.line_map: LineMap = LineMap(source)

    def format_diagnostic(self, diagnostic: Diagnostic):
        line, column = self.line_map.get_location(diagnostic.position)
        return f'{self.file}:{line}:{column}: {diagnostic}'

    def print_diagnostics(self):
        for diagnostic in self.diagnostics:
            print(self.format_diagnostic(diagnostic), file=stdout if diagnostic.kind == 'info' else stderr)
