from typing import Optional

from mattylang.ast import ProgramNode
from mattylang.globals import Globals
from mattylang.lexer import Lexer
from mattylang.module import Module
from mattylang.parser import Parser
from mattylang.symbols import SymbolTable
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker
from mattylang.visitors.emitter import Emitter


class CompileResult:
    def __init__(self, module: Module, ast: ProgramNode, code: Optional[str]):
        self.module, self.ast, self.code = module, ast, code


def compile(file: str, source: str, verbose: bool = False, parse_only: bool = False,
            globals: Optional[SymbolTable] = None) -> CompileResult:
    if globals is None:
        globals = Globals().globals

    module = Module(file, source, globals=Globals().globals, verbose=verbose)
    ast = Parser(Lexer(module)).parse()  # lexical, syntax analysis
    code = None

    if not parse_only:
        ast.accept(Binder(module))
        ast.accept(Checker(module))

        if not module.diagnostics.has_error():
            emitter = Emitter(module)
            ast.accept(emitter)
            code = str(emitter)

    return CompileResult(module, ast, code)

# call after, if compiled in parse_only mode


def check(compile: CompileResult) -> CompileResult:
    compile.ast.accept(Binder(compile.module))
    compile.ast.accept(Checker(compile.module))
    return compile
