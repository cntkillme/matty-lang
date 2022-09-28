#!/usr/bin/env python3
import sys
from typing import List
from compiler.compile import compile
from compiler.lexer import Lexer, Token


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if command == 'help':
        cmd_help()
    elif command == 'run':
        cmd_run()
    elif command == 'test':
        cmd_test()
    elif command == 'tokens':
        cmd_tokens()
    elif command == 'tree':
        cmd_tree()
    elif command == 'bytecode':
        cmd_bytecode()
    else:
        raise NotImplementedError(f'unknown command {command}')


def cmd_help():
    print('Usage')
    print('  matty help                   displays this message')
    print('  matty run [file]             execute a matty source file')
    print('  matty test                   run the test suite')
    print('  matty tokens [file]          prints the tokens')
    print('  matty tree [file] [mode]     prints the abstract syntax tree')
    print('  matty bytecode [file]        prints the bytecode')
    print('Modes')
    print('  The default mode is semcheck.')
    print('  semless      semantic-less mode: semantic analysis is skipped')
    print('  sembind      partial semantic mode: only scoping is performed')
    print('  semcheck     full semantic mode: scoping and type checking is performed')
    print('Notes')
    print('  The stdin file can be specified by explicitly by passing a period as the file name.')
    print('  If a file is unspecified, standard input will be used.')
    print('  The shortcut CTRL + D can be used to terminate standard input.')


def cmd_run():
    file, source = get_file_param(sys.argv[2] if len(sys.argv) > 2 else '')
    _ = compile(file, source)


def cmd_test():
    raise NotImplementedError()


def cmd_tokens():
    _, source = get_file_param(sys.argv[2] if len(sys.argv) > 2 else '')
    scanner = Lexer(source)
    tokens: List[Token] = []
    while scanner.token[0] != 'eof':
        tokens.append(scanner.token)
        scanner.scan()
    print(tokens)


# mode: (run_printer, run_binder, run_checker)
modes = {
    'semless': (True, False, False),
    'sembind': (True, True, False),
    'semcheck': (True, True, True)
}


def cmd_tree():
    file, source = get_file_param(sys.argv[2] if len(sys.argv) > 2 else '')
    mode = sys.argv[3] if len(sys.argv) > 3 else 'semcheck'
    assert mode in modes, f'unknown mode {mode}'
    options = modes[mode]
    _ = compile(file, source, run_printer=options[0], run_binder=options[1], run_checker=options[2])


def cmd_bytecode():
    raise NotImplementedError()


def get_file_param(file: str):
    if file == '' or file == '.':
        return '<stdin>', sys.stdin.read()
    else:
        with open(file, 'r') as f:
            return file, f.read()


if __name__ == '__main__':
    main()
