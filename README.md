# MattyLang
[![test](https://github.com/cntkillme/matty-lang/workmattys/test/badge.svg)](https://github.com/cntkillme/matty-lang/actions)
[![codecov](https://codecov.io/gh/cntkillme/matty-lang/branch/main/graph/badge.svg)](https://codecov.io/gh/cntkillme/matty-lang)

## Introduction
MattyLang is a statically typed programming language designed to explore compiler construction.

## Usage
Stay tuned.

## Testing
In the project's root directory, invoke `$ lua test/init.lua`.

## Syntax Highlighting
The *tmLanguage* can be found [here](/.vscode/matty-syntax/syntaxes/mtl.tmLanguage.json).

## Development Plan
This plan may change as development progresses.

### MattyLang v1
- Lexically-scoped variables, first-class functions, and closures
- Intrinsics variables and functions ($inf, $print, $real2string)
- Primitive literals (nil, bool, real, string)
- Primitive types (Nil, Bool, Real, String) and function types
- Control flow statements (return, if, while, break, continue)
- Common arithmetic, logical, and relational expressions with operator precedence

### MattyLang v2
- Real literal expansion (hexadecimal literals and exponent specifier)
- String escape sequences
- Compound assignment statement
- Intrinsic expansion ($pi, $sin, $substr, etc)

### MattyLang v3
- Labeled break and continue statements
- Arrays, dictionaries, and related intrinsics
- Command-line argument support ($args intrinsic)

### MattyLang v4
- Lambda expressions
- Type aliasing
- Record type
- Tuple type
