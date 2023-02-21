import unittest

from mattylang.linemap import LineMap


class LineMapTest(unittest.TestCase):
    def test(self):
        source = '\nabc\ndef'
        expected_locations = [(1, 1), (2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3)]
        expected_positions = list(range(len(source)))

        linemap = LineMap(source)
        locations = [linemap.get_location(i) for i in range(len(source))]
        self.assertEqual(locations, expected_locations)
        positions = [linemap.get_position(line, column) for line, column in locations]
        self.assertEqual(positions, expected_positions)
