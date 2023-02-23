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
    def __init__(self, module: Module, ast: ProgramNode, code: Optional[str] = None):
        self.module, self.ast, self.code = module, ast, code


def compile(file: str, source: str, verbose: bool = False, no_check: bool = False, no_emit: bool = False,
            globals: Optional[SymbolTable] = None) -> CompileResult:
    if globals is None:
        globals = Globals().globals

    module = Module(file, source, globals=Globals().globals, verbose=verbose)
    result = CompileResult(module, Parser(Lexer(module)).parse())

    if not no_check:
        check(result)

        if not no_emit:
            emit(result)

    return result


def check(compile: CompileResult) -> CompileResult:
    compile.module.diagnostics.next_set()
    compile.ast.accept(Binder(compile.module))
    compile.module.diagnostics.next_set()
    compile.ast.accept(Checker(compile.module))
    compile.module.diagnostics.next_set()
    return compile


def emit(compile: CompileResult) -> CompileResult:
    if not compile.module.diagnostics.has_error():
        compile.module.diagnostics.next_set()
        emitter = Emitter(compile.module)
        compile.ast.accept(emitter)
        compile.code = str(emitter)
        compile.module.diagnostics.next_set()
    return compile
