"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    # TODO: Implement Me
    ran = random.randint(0, 1)
    colours = COLOUR_LIST[:]
    goals = []
    for _ in range(num_goals):
        colour = random.choice(colours)
        colours.remove(colour)
        if ran == 0:
            goals.append(PerimeterGoal(colour))
        else:
            goals.append(BlobGoal(colour))
    return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    # TODO: Implement me
    lst = []
    if len(block.children) == 0:
        for i in range(2 ** (block.max_depth - block.level)):
            sub = []
            for j in range(2 ** (block.max_depth - block.level)):
                sub.append(block.colour)
            lst.append(sub)

        return lst

    for i in range(2 ** (block.max_depth - block.level)):
        sub = []
        for j in range(2 ** (block.max_depth - block.level)):
            if j < 2 ** (block.max_depth - block.level) // 2 and \
                    i < 2 ** (block.max_depth - block.level) // 2:
                sub.append(_flatten(block.children[1])[i][j])
            elif j < 2 ** (block.max_depth - block.level) // 2:
                n = 2 ** (block.max_depth - block.level) // 2
                sub.append(_flatten(block.children[0])[i - n][j])
            elif i < 2 ** (block.max_depth - block.level) // 2:
                n = 2 ** (block.max_depth - block.level) // 2
                sub.append(_flatten(block.children[2])[i][j - n])
            else:
                n = 2 ** (block.max_depth - block.level) // 2
                sub.append(_flatten(block.children[3])[i - n][j - n])
        lst.append(sub)

    return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """
    A perimeter goal in the game of Blocky. The player has to get as many
    unit cells of target colour along the perimeter of the board
     (each worth 1 point). Corners are worth 2 points.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.

    """
    def score(self, board: Block) -> int:
        # TODO: Implement me

        if board.max_depth == 0 and board.colour == self.colour:
            return 4

        lst = _flatten(board)
        score = 0

        for i in range(len(lst)):

            for j in range(len(lst[i])):
                w = len(lst) - 1
                if ((i == 0 and j == 0) or (i == 0 and j == w) or
                        (i == w and j == 0) or (i == w and j == w)) and \
                        lst[i][j] == self.colour:
                    score += 2
                elif (i == 0 or j == 0 or i == w or j == w) and \
                        lst[i][j] == self.colour:
                    score += 1

        return score

    def description(self) -> str:
        # TODO: Implement me
        return f'Perimeter Goal: Try to get as many ' \
               f'{colour_name(self.colour)} ' \
               f'unit blocks around the perimeter of the board. ' \
               f'Corners are double points.'


class BlobGoal(Goal):
    """
        A Blob goal in the game of Blocky. The player has to get the largest
        blob of their target colour possible. See the assignment description
        for what a Blob is.

        === Attributes ===
        colour:
            The target colour for this goal, that is the colour to which
            this goal applies.

        """

    def score(self, board: Block) -> int:
        b = _flatten(board)
        v = []
        for sublist in b:
            sub = []
            for _ in sublist:
                sub.append(-1)
            v.append(sub)
        max_size = 0
        for i in range(len(b)):
            for j in range(len(b[i])):
                size = self._undiscovered_blob_size((i, j), b, v)
                if size > max_size:
                    max_size = size

        return max_size

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        # TODO: Implement me
        i = pos[0]
        j = pos[1]
        if i < 0 or j < 0 or i >= len(board) or j >= len(board):
            return 0
        elif board[i][j] != self.colour:
            visited[i][j] = 0
            return 0
        else:
            size = 1
            visited[i][j] = 1
            if i - 1 >= 0 and visited[i - 1][j] == -1:
                size += self._undiscovered_blob_size((i - 1, j), board, visited)
            if j - 1 >= 0 and visited[i][j - 1] == -1:
                size += self._undiscovered_blob_size((i, j - 1), board, visited)
            if i + 1 < len(board) and visited[i + 1][j] == -1:
                size += self._undiscovered_blob_size((i + 1, j), board, visited)
            if j + 1 < len(board) and visited[i][j + 1] == -1:
                size += self._undiscovered_blob_size((i, j + 1), board, visited)

            return size

    def description(self) -> str:
        # TODO: Implement me
        return f'Blob Goal: Try to get the largest {colour_name(self.colour)}' \
               f' block'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
