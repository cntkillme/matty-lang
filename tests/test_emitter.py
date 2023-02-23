import unittest

from mattylang.ast import *
from mattylang.globals import Globals
from mattylang.module import Module
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker
from mattylang.visitors.emitter import Emitter


class EmitterTest(unittest.TestCase):
    def test_emitter(self):
        self.maxDiff = None
        # fmt: off
        ast = ProgramNode(0, ChunkNode(0, [
            # def x = 1
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 1)),
            # { def x = x x = x }
            ChunkNode(0, [
                VariableDefinitionNode(0, IdentifierNode(0, 'x'), IdentifierNode(0, 'x')),
                VariableAssignmentNode(0, IdentifierNode(0, 'x'), IdentifierNode(0, 'x')),
            ]),
            # if (true) {}
            IfStatementNode(0, BoolLiteralNode(0, True), ChunkNode(0, [])),
            # if (true) print('hi') else print('bye')
            IfStatementNode(0, BoolLiteralNode(0, True),
                ChunkNode(0, [CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [StringLiteralNode(0, 'hi')]))]),
                ChunkNode(0, [CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [StringLiteralNode(0, 'bye')]))]),
            ),
            # while (true) { if (true) continue else break }
            WhileStatementNode(0, BoolLiteralNode(0, True), ChunkNode(0, [
                IfStatementNode(0, BoolLiteralNode(0, True),
                    ChunkNode(0, [ContinueStatementNode(0)]),
                    ChunkNode(0, [BreakStatementNode(0)])),
            ])),
            # def f(n: Real) { if (true) return 0 else return n }
            FunctionDefinitionNode(0, IdentifierNode(0, 'f'),
                [FunctionParameterNode(0, IdentifierNode(0, 'n'), RealTypeNode(0))],
                ChunkNode(0, [IfStatementNode(0, BoolLiteralNode(0, True),
                    ChunkNode(0, [ReturnStatementNode(0, RealLiteralNode(0, 0))]),
                    ChunkNode(0, [ReturnStatementNode(0, IdentifierNode(0, 'n'))]),
                )])
            ),
            # print(f(0))
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [
                CallExpressionNode(0, IdentifierNode(0, 'f'), [RealLiteralNode(0, 0)])
            ])),
            # print(nil)
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [NilLiteralNode(0)])),
            # print(!false || true)
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [
                BinaryExpressionNode(0, '||',
                    UnaryExpressionNode(0, '!', BoolLiteralNode(0, False)),
                    BoolLiteralNode(0, True),
                )
            ])),
        ]))
        # fmt: on

        expected = [
            'x = 1',
            'x_1 = x',
            'x_1 = x_1',
            'if True:',
            '    pass',
            'if True:',
            "    print('hi')",
            'else:',
            "    print('bye')",
            'while True:',
            '    if True:',
            '        continue',
            '    else:',
            '        break',
            'def f(n):',
            '    if True:',
            '        return 0',
            '    else:',
            '        return n',
            'print(f(0))',
            'print(None)',
            'print(((not False) or True))',
        ]

        module = Module('test', '', globals=Globals().globals)
        ast.accept(Binder(module))
        ast.accept(Checker(module))
        emitter = Emitter(module)
        ast.accept(emitter)
        self.assertEqual(str(emitter).splitlines(), expected)
