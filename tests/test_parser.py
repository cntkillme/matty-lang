import unittest

from mattylang.ast import *
from mattylang.module import Module
from mattylang.lexer import Lexer
from mattylang.parser import Parser


class TestParser(unittest.TestCase):
    def make_dict(self, node: AbstractNode):
        tld = node.__dict__.copy()
        for key, value in tld.items():
            if key == 'parent':
                continue

            if isinstance(value, AbstractNode):
                tld[key] = self.make_dict(value)
            elif isinstance(value, list):
                tld[key] = [self.make_dict(item) if isinstance(item, AbstractNode)
                            else item for item in value]  # type: ignore
            elif not isinstance(value, object):
                tld[key] = value

        tld['kind'] = str(node)
        tld['parent'] = None
        return tld

    def test_variables(self):
        self.maxDiff = None
        source = ('\n').join([
            '{',  # 0
            'def x = 1',  # 2
            'x = 2',  # 12
            '}',  # 18
            'def x = -(1+1)*2',  # 20
            'def s = "abc"',  # 37
            'def n = nil',  # 51
        ])

        # fmt: off
        expected = ProgramNode(0, ChunkNode(0, [
            ChunkNode(0, [
                VariableDefinitionNode(2, IdentifierNode(6, 'x'), RealLiteralNode(10, 1.0)),
                VariableAssignmentNode(12, IdentifierNode(12, 'x'), RealLiteralNode(16, 2.0)),
            ]),
            VariableDefinitionNode(20, IdentifierNode(24, 'x'),
                BinaryExpressionNode(28, '*',
                    UnaryExpressionNode(28, '-',
                        BinaryExpressionNode(30, '+',
                            RealLiteralNode(30, 1.0),
                            RealLiteralNode(32, 1.0)
                        ),
                    ),
                    RealLiteralNode(35, 2.0)
                )
            ),
            VariableDefinitionNode(37, IdentifierNode(41, 's'), StringLiteralNode(45, 'abc')),
            VariableDefinitionNode(51, IdentifierNode(55, 'n'), NilLiteralNode(59)),
        ]))
        # fmt: on

        module = Module('test', source)
        ast = Parser(Lexer(module)).parse()
        self.assertEqual(module.diagnostics.has_error(), False, list(module.diagnostics))
        self.assertEqual(self.make_dict(ast), self.make_dict(expected))

    def test_control_flow(self):
        self.maxDiff = None
        source = ('\n').join([
            'while (true)',  # 0
            'if (true) break',  # 13
            'else if (false) continue',  # 29
        ])

        # fmt: off
        expected = ProgramNode(0, ChunkNode(0, [
            WhileStatementNode(0, BoolLiteralNode(7, True), ChunkNode(13, [
                IfStatementNode(13, BoolLiteralNode(17, True),
                    ChunkNode(23, [BreakStatementNode(23)]),
                    ChunkNode(34, [
                        IfStatementNode(34, BoolLiteralNode(38, False), ChunkNode(45, [ContinueStatementNode(45)]))
                    ])
                )
            ]))
        ]))
        # fmt: on

        module = Module('test', source)
        ast = Parser(Lexer(module)).parse()
        self.assertEqual(self.make_dict(ast), self.make_dict(expected))

    def test_function(self):
        self.maxDiff = None
        source = ('\n').join([
            'def f(x: Real, y: Real) { return x + y }',  # 0
            'def z = f(1, 2)',  # 41
            'def hof(f: (Real, Real) -> Real) { return f(1, 2) }',  # 57
        ])

        # fmt: off
        expected = ProgramNode(0, ChunkNode(0, [
            FunctionDefinitionNode(0, IdentifierNode(4, 'f'), [
                FunctionParameterNode(6, IdentifierNode(6, 'x'), RealTypeNode(9)),
                FunctionParameterNode(15, IdentifierNode(15, 'y'), RealTypeNode(18)),
            ], ChunkNode(24, [
                ReturnStatementNode(26, BinaryExpressionNode(33, '+', IdentifierNode(33, 'x'), IdentifierNode(37, 'y')))
            ])),
            VariableDefinitionNode(41, IdentifierNode(45, 'z'), CallExpressionNode(49, IdentifierNode(49, 'f'), [
                RealLiteralNode(51, 1.0),
                RealLiteralNode(54, 2.0),
            ])),
            FunctionDefinitionNode(57, IdentifierNode(61, 'hof'), [
                FunctionParameterNode(65, IdentifierNode(65, 'f'),
                    FunctionTypeNode(68, [RealTypeNode(69), RealTypeNode(75)], RealTypeNode(84))
                )
            ], ChunkNode(90, [
                ReturnStatementNode(92, CallExpressionNode(99, IdentifierNode(99, 'f'), [
                    RealLiteralNode(101, 1.0),
                    RealLiteralNode(104, 2.0),
                ]))
            ]))
        ]))
        # fmt: on

        module = Module('test', source)
        ast = Parser(Lexer(module)).parse()
        self.assertEqual(self.make_dict(ast), self.make_dict(expected))

    def test_types(self):
        self.maxDiff = None
        source = ('\n').join([
            'def f(',  # 0
            'a: Nil,',  # 7
            'b: Real,',  # 15
            'c: String,',  # 24
            'd: Bool,',  # 35
            'e: (Real, Real) -> Real)',  # 44
            '{ }',  # 69
        ])

        # fmt: off
        expected = ProgramNode(0, ChunkNode(0, [
            FunctionDefinitionNode(0, IdentifierNode(4, 'f'), [
                FunctionParameterNode(7, IdentifierNode(7, 'a'), NilTypeNode(10)),
                FunctionParameterNode(15, IdentifierNode(15, 'b'), RealTypeNode(18)),
                FunctionParameterNode(24, IdentifierNode(24, 'c'), StringTypeNode(27)),
                FunctionParameterNode(35, IdentifierNode(35, 'd'), BoolTypeNode(38)),
                FunctionParameterNode(44, IdentifierNode(44, 'e'),
                    FunctionTypeNode(47, [RealTypeNode(48), RealTypeNode(54)], RealTypeNode(63))
                )
            ], ChunkNode(69, []))
        ]))
        # fmt: on

        module = Module('test', source)
        ast = Parser(Lexer(module)).parse()
        self.assertEqual(self.make_dict(ast), self.make_dict(expected))

    def test_diagnostics(self):
        self.maxDiff = None
        source = ('\n').join([
            'def _ = (1+2',
            'def 0',
            'x 0',
            ',',
            'def x = ,',
            'y = ,',
            'if } else }',
            'while }',
            'def f(a:, b,!) }',
            'def x = -}',
            'f(,1+ })',
            'def f(x: (, Real!) -> Nil) { { f(',
        ])

        expected = [
            # line 1
            ('error', 'to close expression'),  # missing )
            # line 2
            ('error', 'expected identifier for definition'),  # missing identifier
            ('error', 'expected = or ( for definition'),  # missing = or (
            ('error', 'unexpected real_literal'),  # unexpected 0
            # line 3
            ('error', 'unexpected identifier'),  # unexpected x
            ('error', 'unexpected real_literal'),  # unexpected 0
            # line 4
            ('error', 'unexpected token ,'),
            # line 5
            ('error', 'to initialize variable x'),  # missing expression
            ('error', 'unexpected token ,'),
            # line 6
            ('error', 'to assign variable y'),  # missing expression
            ('error', 'unexpected token ,'),
            # line 7
            ('error', 'to open if condition'),  # missing (
            ('error', 'to specify if condition'),  # missing expression
            ('error', 'to close if condition'),  # missing )
            ('error', 'unexpected token }'),  # unexpected }
            ('error', 'to specify if body'),  # missing if body statement
            ('error', 'unexpected token }'),  # unexpected }
            ('error', 'to specify else body'),  # missing else body statement
            # line 8
            ('error', 'to open while condition'),  # missing (
            ('error', 'to specify while condition'),  # missing expression
            ('error', 'to close while condition'),  # missing )
            ('error', 'unexpected token }'),  # unexpected }
            ('error', 'to specify while body'),  # missing while body statement
            # line 9
            ('error', 'to specify parameter type'),  # missing type
            ('error', 'to specify parameter type'),  # missing :
            ('error', 'to specify parameter type'),  # missing type
            ('error', 'unexpected ! in parameter list'),  # unexpected !
            ('error', 'to open function body'),  # missing {
            ('error', 'unexpected token }'),  # unexpected }
            # line 10
            ('error', 'expected expression after -'),  # missing expression
            ('error', 'to initialize variable x'),  # missing expression
            ('error', 'unexpected token }'),  # unexpected }
            # line 11
            ('error', 'to specify argument'),  # missing expression
            ('error', 'expected expression'),  # expected expression after +
            ('error', 'expected , or )'),  # missing , or )
            ('error', 'to specify argument'),  # expected expression
            # line 12
            ('error', 'to specify parameter type'),  # missing type
            ('error', 'expected , or ) after type'),  # missing , or )
            ('error', 'to specify parameter type'),  # missing type
            # line 13
            ('error', 'to close function arguments'),  # missing )
            ('error', 'to close block'),  # missing }
            ('error', 'to close function body'),  # missing }
        ]

        module = Module('test', source)
        Parser(Lexer(module)).parse()

        # compare diagnostics
        if len(module.diagnostics) > len(expected):  # pragma: no cover
            expected += [('', '')] * (len(module.diagnostics) - len(expected))

        result = [(diagnostic.kind, expected[idx][1] if diagnostic.message.find(expected[idx][1]) != -
                   1 else diagnostic.message) for idx, diagnostic in enumerate(module.diagnostics)]

        self.assertEqual(result, expected)
