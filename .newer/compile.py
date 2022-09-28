import sys
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.scope import Scope
from compiler.visitors.binder import Binder
from compiler.visitors.checker import Checker
from compiler.visitors.printer import AstPrinter, SymbolPrinter

std_global_scope = Scope()


def compile(file: str, source: str, global_scope: Scope = std_global_scope, run_binder: bool = True, run_checker: bool = True, run_printer: bool = False, run_symbol_printer: bool = False,):
    """Compiler front-end"""
    try:
        assert not run_checker or run_binder, 'cannot run checker without binder'
        file = file
        parser = Parser(Lexer(source))
        binder = Binder(global_scope)
        checker = Checker()
        program = parser.get_program()  # root node

        if run_binder:
            binder = binder.visit_program(program)
            if run_checker:
                checker.visit_program(program)

        if run_printer:
            AstPrinter().visit_program(program)

        return program
    except ValueError as e:
        print(f'{file}: {e.args}', file=sys.stderr)
