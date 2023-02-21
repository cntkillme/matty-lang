import unittest

from mattylang.diagnostics import Diagnostics


class DiagnosticsTest(unittest.TestCase):
    def test(self):
        diagnostics = Diagnostics(verbose=True)
        diagnostics.emit_diagnostic('info', 'info message', 0)
        diagnostics.emit_diagnostic('warning', 'warning message', 1)
        self.assertEqual(diagnostics.has_error(), False)
        diagnostics.emit_diagnostic('error', 'error message', 2)
        self.assertEqual(diagnostics.has_error(), True)
        diagnostics.sort()
        self.assertEqual(list(map(lambda d: d.kind, list(diagnostics))), ['info', 'warning', 'error'])
        self.assertEqual(list(map(lambda d: d.kind if str(d).find(
            f'{d.kind} message') != -1 else str(d), list(diagnostics))), ['info', 'warning', 'error'])
