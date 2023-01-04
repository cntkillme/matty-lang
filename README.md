# MattyLang

## Introduction
MattyLang is a statically typed programming language designed to explore compiler construction and type systems.

## Usage
See `$ ./matty.py help`, quick start: `$ ./matty.py --syntax examples/v0.0.1.mtl`.

```
usage: matty.py [-h] [-o OUTPUT] [-V] [-v] [--tokens] [--syntax] [--symbols] [--code] [file]

MattyLang frontend, compiles and executes MattyLang files.

positional arguments:
  file                  the input file (none for REPL)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        the output file
  -V, --version         show program's version number and exit
  -v, --verbose         verbose output
  --tokens              print the tokens
  --syntax              print the syntax tree
  --symbols             print the symbol table
  --code                print the generated code
```

Note: if a file is unspecified, standard input will be used.
The shortcut CTRL + D (Universal) or CTRL + Z (Windows) can be used to terminate standard input.

## Testing
In the project's root directory, invoke `$ python -m unittest discover tests`.
To generate a coverage report, invoke `$ python -m coverage run -m unittest discover tests` and then `$ coverage report`.

## Syntax Highlighting
The *tmLanguage* can be found [here](/.vscode/matty-syntax/syntaxes/mtl.tmLanguage.json).

## Development Plan
See: [TODO.md](/TODO.md) and [grammar.ebnf](/doc/grammar.ebnf)
