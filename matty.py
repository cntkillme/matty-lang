#!/usr/bin/env python3
import argparse
from typing import List

from mattylang.lexer import Lexer, Token
from mattylang.module import Module
from mattylang.parser import Parser
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker
from mattylang.visitors.emitter import Emitter
from mattylang.visitors.printer import Printer, SymbolPrinter


def main() -> None:
    parser = argparse.ArgumentParser(description='MattyLang frontend, compiles and executes MattyLang files.')
    parser.add_argument('file', type=str, nargs='?', help='the input file (none for REPL)')
    parser.add_argument('-o', '--output', type=str, help='the output file')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('--tokens', action='store_true', help='print the tokens')
    parser.add_argument('--syntax', action='store_true', help='print the syntax tree')
    parser.add_argument('--symbols', action='store_true', help='print the symbol table')
    parser.add_argument('--code', action='store_true', help='print the generated code')
    parser.add_argument('--no-analysis', action='store_true', help='skip semantic analysis')
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
            run(parsed, 'stdin', source)
        except EOFError:
            break


def get_tokens(file: str, source: str):
    module = Module(file, source)
    lexer = Lexer(module)
    tokens: List[Token] = []
    while lexer.peek().kind != 'eof':
        tokens.append(lexer.peek())
        lexer.scan()
    return tokens


def run(args: argparse.Namespace, file: str, source: str):
    module = Module(file, source, verbose=args.verbose)

    if args.tokens:
        tokens = get_tokens(file, source)
        for token in tokens:
            line, column = module.line_map.get_location(token.position)
            print(f'{file}:{line}:{column}: {token}')

    program = Parser(Lexer(module)).parse()

    if not args.no_analysis:
        program.accept(Binder(module))
        program.accept(Checker(module))

    if args.syntax:
        program.accept(Printer(module))

    if args.symbols:
        program.accept(SymbolPrinter(module))

    if module.diagnostics.has_error():
        module.diagnostics.sort()
        module.print_diagnostics()
        return 1

    if args.no_analysis:
        return 0

    emitter = Emitter(module)
    program.accept(emitter)

    module.diagnostics.sort()
    module.print_diagnostics()

    if module.diagnostics.has_error():
        return 1

    if args.code:
        print(str(emitter))

    if args.output:
        with open(args.output, 'w') as fd:
            fd.write(str(emitter))

    return 0


if __name__ == '__main__':
    main()
