# MattyLang

## Introduction
MattyLang is a statically typed programming language designed to explore compiler construction and type systems.
MattyLang v1 is the Capstone goal, further versions may be developed in the future.

## Usage
See `matty help`, quick start: `$ matty examples/v0.0.1.mtl`.

Note: if a file is unspecified, standard input will be used.
The shortcut CTRL + D or CTRL + Z can be used to terminate standard input.

## Testing
In the project's root directory, invoke `$ python test.lua`.

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
- Intrinsic expansion ($pi, $sin, $substr, etc)
- Labeled break and continue statements
- Arrays and dictionaries
- Index and index-assign expressions (implies qualified name expansion)
- Lambda expressions
- Type aliasing
- Record type
- Tuple type
- ...
