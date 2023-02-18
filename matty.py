#!/usr/bin/env python3
import argparse

from mattylang.globals import Globals
from mattylang.lexer import Lexer
from mattylang.module import Module
from mattylang.parser import Parser
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker
from mattylang.visitors.emitter import Emitter
from mattylang.visitors.printers import AstPrinter, SymbolPrinter


def main() -> None:
    parser = argparse.ArgumentParser(description='MattyLang frontend, compiles and executes MattyLang files.')
    parser.add_argument('file', type=str, nargs='?', help='the input file (none for REPL)')
    parser.add_argument('-o', '--output', type=str, help='the output file (default is <file>.py)')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('--tokens', action='store_true', help='print the tokens')
    parser.add_argument('--syntax', action='store_true', help='print the syntax tree')
    parser.add_argument('--symbols', action='store_true', help='print the symbol table')
    parser.add_argument('--code', action='store_true', help='print the generated code')
    parser.add_argument('--parse-only', action='store_true', help='skip semantic analysis and code generation')
    parsed = parser.parse_args()

    if parsed.file:
        with open(parsed.file, 'r') as file:
            source = file.read()
        run(parsed, parsed.file, source)
        return

    # REPL
    while True:
        try:
            source = input('> ')
            run(parsed, 'stdin', source, no_default_output=True)
        except EOFError:
            break


def run(args: argparse.Namespace, file: str, source: str, no_default_output: bool = False):
    module = Module(file, source, globals=Globals().globals, verbose=args.verbose)

    if args.tokens:
        lexer = Lexer(module)
        while lexer.peek().kind != 'eof':
            line, column = module.line_map.get_location(lexer.peek().position)
            print(f'{file}:{line}:{column}: {lexer.peek()}')
            lexer.scan()

        module.reset()  # reset module (clears diagnostics)

    program = Parser(Lexer(module)).parse()  # lexical, syntax analysis

    if not args.parse_only:
        program.accept(Binder(module))  # semantic analysis: symbol binding/name resolution
        program.accept(Checker(module))  # semantic analysis: type binding/type checking and inference

    if args.syntax:
        program.accept(AstPrinter(module))

    if args.symbols:
        program.accept(SymbolPrinter(module))

    if module.diagnostics.has_error():
        module.print_diagnostics()
        return 1
    elif args.parse_only:
        module.print_diagnostics()
        return 0

    emitter = Emitter(module)
    program.accept(emitter)  # code generation
    module.print_diagnostics()

    if module.diagnostics.has_error():
        return 1

    if args.code:
        print(str(emitter))

    if args.output:
        new_file = args.output
    elif not no_default_output:
        new_file = file.split('/')[-1].split('\\')[-1]  # get file name
        new_file = new_file.rsplit('.mtl', 1)[0] + '.py'  # remove .mtl extension, add .py extension

        with open(new_file, 'w') as fd:
            fd.write(str(emitter))

    return 0


if __name__ == '__main__':
    main()
