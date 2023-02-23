#!/usr/bin/env python3
import argparse

from mattylang import compile
from mattylang.globals import Globals
from mattylang.lexer import Lexer
from mattylang.module import Module
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
            run(parsed, 'stdin', source, no_file_output=True)
        except EOFError:
            break


def run(args: argparse.Namespace, file: str, source: str, no_file_output: bool = False):
    if args.tokens:
        module = Module(file, source, globals=Globals().globals, verbose=args.verbose)
        lexer = Lexer(module)
        while lexer.peek().kind != 'eof':
            line, column = module.line_map.get_location(lexer.token_position())
            print(f'{file}:{line}:{column}: {lexer.peek()}')
            lexer.scan()

    result = compile(file, source, verbose=args.verbose, no_check=args.parse_only, globals=Globals().globals)

    if args.syntax:
        result.ast.accept(AstPrinter(result.module))

    if args.symbols:
        SymbolPrinter(result.module)

    if args.code and result.code is not None:
        print(result.code)

    if not no_file_output:
        if args.output:
            new_file = args.output

        if result.code is not None:
            new_file = file.split('/')[-1].split('\\')[-1]  # get file name
            new_file = new_file.rsplit('.mtl', 1)[0] + '.py'  # remove .mtl extension, add .py extension

            with open(new_file, 'w') as fd:
                fd.write(result.code)

    if result.code is not None:
        exec(result.code, globals(), globals())

    result.module.print_diagnostics()
    return 1 if result.module.diagnostics.has_error() else 0


if __name__ == '__main__':
    main()
