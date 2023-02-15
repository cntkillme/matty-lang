from bisect import bisect_right
from typing import Tuple


class LineMap:
    """
    A memory-efficient data structure that provides a mapping between character positions and their location (line, column).
    This allows for only the position to be stored per node, reducing complexity and overall memory usage.
    """

    # Time Complexity: Θ(len(string))
    # Space Complexity: Θ(count('\n'))
    def __init__(self, string: str):
        self.__line_starts = [0] + [i + 1 for i, c in enumerate(string) if c == '\n']

    # Time Complexity: Θ(1)
    def get_position(self, line: int, column: int = 1) -> int:
        return self.__line_starts[line - 1] + (column - 1)

    # Time Complexity: O(log(count('\n')))
    def get_line(self, position: int) -> int:
        return bisect_right(self.__line_starts, position)

    # Time Complexity: O(log(count('\n')))
    def get_column(self, position: int) -> int:
        return 1 + (position - self.__line_starts[self.get_line(position) - 1])

    # Time Complexity: O(log(count('\n')))
    def get_location(self, position: int) -> Tuple[int, int]:
        line = self.get_line(position)
        column = 1 + (position - self.__line_starts[line - 1])
        return line, column
