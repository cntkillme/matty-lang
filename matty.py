#!/usr/bin/env python3
import argparse
from typing import List

from mattylang.module import Module
from mattylang.lexer import Lexer, Token
from mattylang.parser import Parser
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker
from mattylang.visitors.printer import Printer, SymbolPrinter


def main() -> None:
    parser = argparse.ArgumentParser(description='MattyLang frontend, compiles and executes MattyLang files.')
    parser.add_argument('file', type=str, nargs='?', help='the input file (none for REPL)')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('--tokens', action='store_true', help='print the tokens')
    parser.add_argument('--syntax', action='store_true', help='print the syntax tree')
    parser.add_argument('--symbols', action='store_true', help='print the symbol table')
    parser.add_argument('--globals', action='store_true', help='print the global table')
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
    token = lexer.token
    while token.kind != 'eof':
        tokens.append(token)
        token = lexer.scan()
    return tokens


def run(args: argparse.Namespace, file: str, source: str) -> None:
    module = Module(file, source, verbose=args.verbose)

    if args.tokens:
        tokens = get_tokens(file, source)
        print('\n'.join(map(str, tokens)))

    lexer = Lexer(module)
    parser = Parser(lexer)
    program = parser.program
    program.accept(Binder(module))
    program.accept(Checker(module))

    if args.syntax:
        program.accept(Printer(module))

    if args.symbols:
        program.accept(SymbolPrinter(module))

    if args.globals:
        print('{')
        for symbol in module.globals.symbols.values():
            print('  ' + str(symbol))
        print('}')

    # show diagnostics
    module.print_diagnostics()


if __name__ == '__main__':
    main()
