"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    # TODO: Implement Me
    total_players = num_human + num_random + len(smart_players)
    goals = generate_goals(total_players)
    players = []
    for i in range(total_players):
        if 0 <= i < num_human:
            players.append(HumanPlayer(i, goals[i]))
        elif num_human <= i < num_human + num_random:
            players.append(RandomPlayer(i, goals[i]))
        else:
            players.append(SmartPlayer(i, goals[i],
                                       smart_players[i - num_random -
                                                     num_human]))
    return players


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    # TODO: Implement me
    x = location[0]
    y = location[1]
    b_x = block.position[0]
    b_y = block.position[1]
    if block.level == level and b_x <= x < b_x + block.size and \
            b_y <= y < b_y + block.size:
        return block
    elif level > block.level and b_x <= x < b_x + block.size and \
            b_y <= y < b_y + block.size and len(block.children) == 0:
        return block
    elif block.level == level:
        return None
    for child in block.children:
        if _get_block(child, location, level) is not None:
            return _get_block(child, location, level)
    return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """
    A computer-player that generates a random but valid move on a random block.
    === Private Attributes ===
    _proceed:
      True when the player should make a move, False when the player should
      wait.
    """

    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        # TODO: Implement Me
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        # TODO: Implement Me
        b = board.create_copy()
        valid = False
        move = ('', -1)
        location = (-1, -1)
        level = -1
        while not valid:
            move = random.choice([ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE,
                                  SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT,
                                  COMBINE])

            location = (random.randint(0, b.size - 1),
                        random.randint(0, b.size - 1))
            level = random.randint(0, b.max_depth)
            block = _get_block(b, location, level)

            if block is not None and \
                    ((move == ROTATE_CLOCKWISE and block.rotate(1)) or
                     (move == ROTATE_COUNTER_CLOCKWISE and block.rotate(3)) or
                     (move == SWAP_HORIZONTAL and block.swap(0)) or
                     (move == SWAP_VERTICAL and block.swap(1)) or
                     (move == SMASH and block.smash()) or
                     (move == PAINT and block.paint(self.goal.colour)) or
                     (move == COMBINE and block.combine())):
                valid = True

        self._proceed = False  # Must set to False before returning!
        return _create_move(move, _get_block(board, location, level))


class SmartPlayer(Player):
    """
    A smart player is a computer-player that generates <_difficulty> moves and
    plays the best one. See assignment description for more details.
    === Private Attributes ===
    _proceed:
      True when the player should make a move, False when the player should
      wait.
    _difficulty: the number of options for moves the smart player has
    """

    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        # TODO: Implement Me
        Player.__init__(self, player_id, goal)
        self._proceed = False
        self._difficulty = difficulty

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        # TODO: Implement Me
        n, scores, blocks, moves = 0, [], [], []
        while (
                board.max_depth > 0 or (
                    board.colour != self.goal.colour and board.max_depth == 0)
        ) and n < self._difficulty:
            b = board.create_copy()
            move = random.choice([ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE,
                                  SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT,
                                  COMBINE])

            location = (random.randint(0, b.size - 1),
                        random.randint(0, b.size - 1))
            level = random.randint(0, b.max_depth)
            block = _get_block(b, location, level)

            if block is not None and \
                    ((move == ROTATE_CLOCKWISE and block.rotate(1)) or
                     (move == ROTATE_COUNTER_CLOCKWISE and block.rotate(3)) or
                     (move == SWAP_HORIZONTAL and block.swap(0)) or
                     (move == SWAP_VERTICAL and block.swap(1)) or
                     (move == SMASH and block.smash()) or
                     (move == PAINT and block.paint(self.goal.colour)) or
                     (move == COMBINE and block.combine())):
                scores.append(self.goal.score(b))
                blocks.append(block)
                moves.append(move)
                n += 1

        if len(scores) == 0 or max(scores) <= self.goal.score(board):
            self._proceed = False
            return _create_move(PASS, board)
        else:
            max_i = 0
            max_score = -1
            for i in range(len(scores)):
                if scores[i] > max_score:
                    max_i = i
                    max_score = scores[i]
            move = moves[max_i]
            block = blocks[max_i]

        self._proceed = False  # Must set to False before returning!
        return _create_move(move, _get_block(board, block.position,
                                             block.level))


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
