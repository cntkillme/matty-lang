#!/usr/bin/env python3
import argparse
import sys

from mattylang.module import Module
from mattylang.lexer import Lexer
from mattylang.iterator import *


def main() -> None:
    parser = argparse.ArgumentParser(description='MattyLang frontend, compiles and executes MattyLang files.')
    parser.add_argument('file', type=str, nargs='?', help='the input file (none for REPL)')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('--tokens', action='store_true', help='print the tokens')
    parser.add_argument('--tree', choices=['undecorated', 'decorated'], help='print the syntax tree')
    parser.add_argument('--symbols', action='store_true', help='print the symbol table')
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


def run(args: argparse.Namespace, file: str, source: str) -> None:
    module = Module(file, source, verbose=args.verbose)

    if args.tokens:
        lexer = Lexer(module)
        tokens = list(TokenIterator(lexer))
        print(' '.join(map(str, tokens)))

    # TODO: parse

    if args.tree == 'undecorated':
        raise NotImplementedError()

    # TODO: bind and type-check

    if args.tree == 'decorated':
        raise NotImplementedError()

    if args.symbols:
        raise NotImplementedError()

    # show diagnostics
    print_diagnostics(module)


def print_diagnostics(module: Module):
    for diagnostic in module.get_diagnostics():
        diagnostic.print(module.get_file())


if __name__ == '__main__':
    main()
