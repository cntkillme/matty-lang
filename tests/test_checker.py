import unittest

from mattylang.ast import *
from mattylang.globals import Globals
from mattylang.module import Module
from mattylang.visitors.binder import Binder
from mattylang.visitors.checker import Checker


class CheckerTest(unittest.TestCase):
    def test_checker(self):
        self.maxDiff = None
        # fmt: off
        ast = ChunkNode(0, [
            # def x = 1
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 1)),
            # x = (x % 2) + ((1 - 1) * (1 / 1))
            VariableAssignmentNode(0, IdentifierNode(0, 'x'),
                BinaryExpressionNode(0, '+',
                    BinaryExpressionNode(0, '%', IdentifierNode(0, 'x'), RealLiteralNode(0, 2)),
                    BinaryExpressionNode(0, '*',
                        BinaryExpressionNode(0, '-', RealLiteralNode(0, 1), RealLiteralNode(0, 1)),
                        BinaryExpressionNode(0, '/', RealLiteralNode(0, 1), RealLiteralNode(0, 1))
                    )
            )),
            # def _true = ((nil == nil) == true) != false) && !(1 < 2 || 1 >= 2 || 2 >= 1 || 2 <= 1)
            VariableDefinitionNode(0, IdentifierNode(0, '_true'),
                BinaryExpressionNode(0, '&&',
                    BinaryExpressionNode(0, '!=',
                        BinaryExpressionNode(0, '==',
                            BinaryExpressionNode(0, '==', NilLiteralNode(0), NilLiteralNode(0)),
                            BoolLiteralNode(0, True)
                        ),
                        BoolLiteralNode(0, False)
                    ),
                    UnaryExpressionNode(0, '!',
                        BinaryExpressionNode(0, '||',
                            BinaryExpressionNode(0, '||',
                                BinaryExpressionNode(0, '||',
                                    BinaryExpressionNode(0, '<', RealLiteralNode(0, 1), RealLiteralNode(0, 2)),
                                    BinaryExpressionNode(0, '>=', RealLiteralNode(0, 1), RealLiteralNode(0, 2))
                                ),
                                BinaryExpressionNode(0, '>=', RealLiteralNode(0, 2), RealLiteralNode(0, 1))
                            ),
                            BinaryExpressionNode(0, '<=', RealLiteralNode(0, 2), RealLiteralNode(0, 1))
                        )
                    ),
            )),
            # def f(n: Real) { if (true) return }
            FunctionDefinitionNode(0, IdentifierNode(0, 'f'),
                [FunctionParameterNode(0, IdentifierNode(0, 'n'), RealTypeNode(0))], ChunkNode(0, [
                    IfStatementNode(0, BoolLiteralNode(0, True), ChunkNode(0, [ReturnStatementNode(0)]))
            ])),
            # def g(n: Real) { if (n < 5) return g(n) + 1 return n }
            FunctionDefinitionNode(0, IdentifierNode(0, 'g'),
                [FunctionParameterNode(0, IdentifierNode(0, 'n'), RealTypeNode(0))], ChunkNode(0, [
                IfStatementNode(0,
                    BinaryExpressionNode(0, '<', IdentifierNode(0, 'n'), RealLiteralNode(0, 5)),
                    ChunkNode(0, [
                        ReturnStatementNode(0,
                            BinaryExpressionNode(0, '+',
                                CallExpressionNode(0, IdentifierNode(0, 'g'), [IdentifierNode(0, 'n')]),
                                RealLiteralNode(0, 1)
                            )
                        )
                ])),
                ReturnStatementNode(0, IdentifierNode(0, 'n'))
            ])),
            # while (false) if (true) continue else break
            WhileStatementNode(0, BoolLiteralNode(0, False), ChunkNode(0, [
                IfStatementNode(0, BoolLiteralNode(0, True),
                    ChunkNode(0, [ContinueStatementNode(0)]),
                    ChunkNode(0, [BreakStatementNode(0)]))
            ])),
            # print(g(-3))
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'print'), [
                CallExpressionNode(0, IdentifierNode(0, 'g'), [RealLiteralNode(0, 3)])
            ])),
            # def empty() {}
            FunctionDefinitionNode(0, IdentifierNode(0, 'empty'), [], ChunkNode(0, [])),
        ])

        # fmt: on

        module = Module('test', '', globals=Globals().globals)
        ast.accept(Binder(module))
        ast.accept(Checker(module))

        self.assertEqual(len(module.diagnostics), 0)

    def test_diagnostics(self):
        self.maxDiff = None
        # fmt: off
        ast = ChunkNode(0, [
            # def x = 1
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 1)),
            # x = "a"
            VariableAssignmentNode(0, IdentifierNode(0, 'x'), StringLiteralNode(0, 'a')),
            # if (x) {}
            IfStatementNode(0, IdentifierNode(0, 'x'), ChunkNode(0, [])),
            # while (x) {}
            WhileStatementNode(0, IdentifierNode(0, 'x'), ChunkNode(0, [])),
            # break
            BreakStatementNode(0),
            # continue
            ContinueStatementNode(0),
            # def f() { if (true) return 1 }
            FunctionDefinitionNode(0, IdentifierNode(0, 'f'), [], ChunkNode(0, [
                IfStatementNode(0, BoolLiteralNode(0, True), ChunkNode(0, [
                    ReturnStatementNode(0, RealLiteralNode(0, 1))
                ]))
            ])),
            # return
            ReturnStatementNode(0, None),
            # f(1)
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'f'), [RealLiteralNode(0, 1)])),
            # def a1 = -"str"
            VariableDefinitionNode(0, IdentifierNode(0, 'a1'), UnaryExpressionNode(0, '-', StringLiteralNode(0, 'str'))),
            # def a3 = !0
            VariableDefinitionNode(0, IdentifierNode(0, 'a3'), UnaryExpressionNode(0, '!', RealLiteralNode(0, 0))),
            # def a2 = 1 + "a"
            VariableDefinitionNode(0, IdentifierNode(0, 'a2'), BinaryExpressionNode(0, '+', RealLiteralNode(0, 1), StringLiteralNode(0, 'a'))),
            # def g() { if (true) return 1 return 'a' }
            FunctionDefinitionNode(0, IdentifierNode(0, 'g'), [], ChunkNode(0, [
                IfStatementNode(0, BoolLiteralNode(0, True), ChunkNode(0, [ReturnStatementNode(0, RealLiteralNode(0, 1))])),
                ReturnStatementNode(0, StringLiteralNode(0, 'a'))
            ])),
            # def h() { { return 0 } { return 'a' } return 0 }
            FunctionDefinitionNode(0, IdentifierNode(0, 'h'), [], ChunkNode(0, [
                ChunkNode(0, [ReturnStatementNode(0, RealLiteralNode(0, 0))]),
                ChunkNode(0, [ReturnStatementNode(0, StringLiteralNode(0, 'a'))]),
                ReturnStatementNode(0, RealLiteralNode(0, 0))
            ])),
            # x()
            CallStatementNode(0, CallExpressionNode(0, IdentifierNode(0, 'x'), [])),
        ])
        # fmt: on

        expected = [
            ('error', 'incompatible types for assignment'),
            ('error', 'expected type of condition to be Bool'),
            ('error', 'expected type of condition to be Bool'),
            ('error', 'break statement outside of loop'),
            ('error', 'continue statement outside of loop'),
            ('error', 'function must return a value'),
            ('error', 'return statement outside of function'),
            ('error', 'incompatible arguments for function call'),
            ('warning', 'return value discarded'),
            ('error', 'incompatible operand type for expression'),
            ('error', 'incompatible operand type for expression'),
            ('error', 'incompatible operand types for expression'),
            ('error', 'incompatible return type'),
            ('error', 'incompatible return type'),
            ('error', 'expected function type when calling'),
        ]

        module = Module('test', '')
        ast.accept(Binder(module))
        ast.accept(Checker(module))

        # compare diagnostics
        if len(module.diagnostics) > len(expected):  # pragma: no cover
            expected += [('', '')] * (len(module.diagnostics) - len(expected))

        result = [(diagnostic.kind, expected[idx][1] if diagnostic.message.find(expected[idx][1]) != -
                   1 else diagnostic.message) for idx, diagnostic in enumerate(module.diagnostics)]

        self.assertEqual(result, expected)
