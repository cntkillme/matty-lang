# MattyLang

## Introduction
MattyLang is a statically typed programming language designed to explore compiler construction and type systems.
MattyLang v1 is the Capstone goal, further versions may be developed in the future.

## Usage
See `$ ./matty.py help`, quick start: `$ ./matty.py --syntax examples/v0.0.1.mtl`.

```
usage: matty.py [-h] [-V] [-v] [--tokens] [--syntax] [--symbols] [file]

MattyLang frontend, compiles and executes MattyLang files.

positional arguments:
  file           the input file (none for REPL)

options:
  -h, --help     show this help message and exit
  -V, --version  show program's version number and exit
  -v, --verbose  verbose output
  --tokens       print the tokens
  --syntax       print the syntax tree
  --symbols      print the symbol table
  --globals      print the global table
```

Note: if a file is unspecified, standard input will be used.
The shortcut CTRL + D (Universal) or CTRL + Z (Windows) can be used to terminate standard input.

## Testing
In the project's root directory, invoke `$ python -m unittest discover tests`.

Coverage: `$ python -m coverage run -m unittest discover tests ; python -m coverage report`

## Syntax Highlighting
The *tmLanguage* can be found [here](/.vscode/matty-syntax/syntaxes/mtl.tmLanguage.json).

## Development Plan
See: [TODO.md](/TODO.md) and [grammar.ebnf](/doc/grammar.ebnf)

## Future Plans
- CI and Code Coverage
- Closures and Lambdas
- Command-line argument support ($args intrinsic)
- Real literal expansion (hexadecimal literals and exponent specifier)
- String escape sequences
- Compound assignment statements
- Intrinsic expansion ($pi, $sin, etc)
- Labeled break and continue statements
- Arrays and dictionaries
- Index and index-assign expressions (implies qualified name expansion)
- Lambda expressions
- Type aliasing
- Record type
- Tuple type
- ...
