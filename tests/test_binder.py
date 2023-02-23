import unittest
from typing import Any, cast

from mattylang.ast import *
from mattylang.globals import Globals
from mattylang.module import Module
from mattylang.visitors.binder import Binder


class BinderTest(unittest.TestCase):
    def test_binder(self):
        # fmt: off
        ast = ChunkNode(0, [
            # def x = 10
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 10)),
            # def f(n: Real) { def n = n print(f(n)) }
            FunctionDefinitionNode(0, IdentifierNode(0, 'f'),
                [FunctionParameterNode(0, IdentifierNode(0, 'n'), RealTypeNode(0))],
                ChunkNode(0, [
                    VariableDefinitionNode(0, IdentifierNode(0, 'n'), IdentifierNode(0, 'n')),
                    CallStatementNode(0,
                        CallExpressionNode(0, IdentifierNode(0, 'print'), [
                            CallExpressionNode(0, IdentifierNode(0, 'f'), [IdentifierNode(0, 'n')])
                        ])
                    )
                ])
            ),
        ])
        # fmt: on
        ast_view = cast(Any, ast)
        id_x = ast_view.statements[0].identifier
        id_f = ast_view.statements[1].identifier
        id_param_n = ast_view.statements[1].parameters[0].identifier
        id_var_n = ast_view.statements[1].body.statements[0].identifier
        id_var_n_init = ast_view.statements[1].body.statements[0].initializer
        id_print_call = ast_view.statements[1].body.statements[1].call_expression.identifier
        id_f_call = ast_view.statements[1].body.statements[1].call_expression.arguments[0].identifier
        id_f_call_arg = ast_view.statements[1].body.statements[1].call_expression.arguments[0].arguments[0]

        module = Module('test', '', globals=Globals().globals)
        ast.accept(Binder(module))
        self.assertEqual(len(module.diagnostics), 0)

        # all identifiers have symbols
        self.assertIsNotNone(id_x.symbol)
        self.assertIsNotNone(id_f.symbol)
        self.assertIsNotNone(id_param_n.symbol)
        self.assertIsNotNone(id_var_n.symbol)
        self.assertIsNotNone(id_var_n_init.symbol)
        self.assertIsNotNone(id_print_call.symbol)
        self.assertIsNotNone(id_f_call.symbol)
        self.assertIsNotNone(id_f_call_arg.symbol)

        # scoping rules are correct
        self.assertNotEqual(id_param_n.symbol, id_var_n.symbol)
        self.assertEqual(id_var_n_init.symbol, id_param_n.symbol)
        self.assertEqual(id_f_call.symbol, id_f.symbol)
        self.assertEqual(id_f_call_arg.symbol, id_var_n.symbol)

    def test_diagnostics(self):
        ast = ChunkNode(0, [
            # duplicate definition
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 10)),
            VariableDefinitionNode(0, IdentifierNode(0, 'x'), RealLiteralNode(0, 10)),  # duplicate definition
            FunctionDefinitionNode(0, IdentifierNode(0, 'x'), [], ChunkNode(0, [])),  # duplicate definition
            # duplicate parameter
            FunctionDefinitionNode(0, IdentifierNode(0, 'f'), [
                FunctionParameterNode(0, IdentifierNode(0, 'n'), BoolTypeNode(0)),
                FunctionParameterNode(0, IdentifierNode(0, 'n'), RealTypeNode(0)),
            ], ChunkNode(0, [])),
            # undefined reference
            VariableDefinitionNode(0, IdentifierNode(0, 'y'), IdentifierNode(0, 'y')),  # undefined reference
        ])

        expected = [
            ('error', 'analysis: duplicate definition of x'),
            ('error', 'analysis: duplicate definition of x'),
            ('error', 'analysis: duplicate parameter n'),
            ('error', 'analysis: undefined reference to y'),
        ]

        module = Module('test', '')
        ast.accept(Binder(module))

        # compare diagnostics
        if len(module.diagnostics) > len(expected):  # pragma: no cover
            expected += [('', '')] * (len(module.diagnostics) - len(expected))

        result = [(diagnostic.kind, expected[idx][1] if diagnostic.message.find(expected[idx][1]) != -
                   1 else diagnostic.message) for idx, diagnostic in enumerate(module.diagnostics)]

        self.assertEqual(result, expected)
