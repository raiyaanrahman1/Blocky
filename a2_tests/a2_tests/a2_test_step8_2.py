import unittest
from a2_test import A2Test, block_bfs
from block import random as player_random
import block
from player import *
from goal import *

SEED_NUMBER = 1214
from unittest.mock import patch
import sys
sys.setrecursionlimit(2000)


class TestCreateCopy(A2Test):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_copy_leaf(self):
        copy = self.leaf_block.create_copy()
        exp_list = [getattr(self.leaf_block, attr_name) for attr_name in self.block_attrs]
        exp_list[-1] = len(copy.children)
        self.assertBlock(copy, exp_list, True, True)
        self.assertFalse(id(copy) == id(self.leaf_block))

    def test_copy_one_level(self):
        copy = self.one_level.create_copy()
        self.assertBlock(copy, [(0, 0), 10, None, 0, 1, 4], True, False)
        self.assertBlock(copy.children[0], [(5, 0), 5, (20, 20, 20), 1, 1, 0], True, True)
        self.assertBlock(copy.children[1], [(0, 0), 5, (30, 30, 30), 1, 1, 0], True, True)
        self.assertBlock(copy.children[2], [(0, 5), 5, (40, 40, 40), 1, 1, 0], True, True)
        self.assertBlock(copy.children[3], [(5, 5), 5, (50, 50, 50), 1, 1, 0], True, True)
        org_bfs_ids = list(map(lambda x: id(x), block_bfs(self.one_level)))
        copy_bfs = list(map(lambda x: id(x), block_bfs(copy)))
        self.assertTrue(len(org_bfs_ids) == len(copy_bfs))
        self.assertFalse(any([id_ in org_bfs_ids for id_ in copy_bfs]),
                         "You should not have any id from the original block")

    def test_copy_one_internal(self):
        copy = self.one_internal.create_copy()
        self.assertBlock(copy, [(0, 0), 100, None, 0, 2, 4], True, False)
        self.assertBlock(copy.children[0], [(50, 0), 50, None, 1, 2, 4], True, False)
        self.assertBlock(copy.children[1], [(0, 0), 50, (80, 80, 80), 1, 2, 0], True, True)
        self.assertBlock(copy.children[2], [(0, 50), 50, (70, 70, 70), 1, 2, 0], True, True)
        self.assertBlock(copy.children[3], [(50, 50), 50, (60, 60, 60), 1, 2, 0], True, True)
        self.assertBlock(copy.children[0].children[0], [(75, 0), 25, (40, 40, 40), 2, 2, 0], True, True)
        self.assertBlock(copy.children[0].children[1], [(50, 0), 25, (30, 30, 30), 2, 2, 0], True, True)
        self.assertBlock(copy.children[0].children[2], [(50, 25), 25, (20, 20, 20), 2, 2, 0], True, True)
        self.assertBlock(copy.children[0].children[3], [(75, 25), 25, (10, 10, 10), 2, 2, 0], True, True)
        org_bfs_ids = list(map(lambda x: id(x), block_bfs(self.one_internal)))
        copy_bfs = list(map(lambda x: id(x), block_bfs(copy)))
        self.assertTrue(len(org_bfs_ids) == len(copy_bfs))
        self.assertFalse(any([id_ in org_bfs_ids for id_ in copy_bfs]),
                         "You should not have any id from the original block")


class A2TestPlayerTopLevel(A2Test):
    def setUp(self) -> None:
        # player_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        # player_random.seed(SEED_NUMBER)
        super().tearDown()

    def create_player(self, id_, goal, difficulty):
        player = SmartPlayer(id_, goal, difficulty)
        player._proceed = True
        return player

    def do_action(self, block: Block, action: Tuple[str, Optional[int]],
                  target_color: Tuple[int, int, int]) -> bool:
        move_successful = False
        direction = action[1]
        if action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
            move_successful = block.rotate(direction)
        elif action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
            move_successful = block.swap(direction)
        elif action == SMASH:
            move_successful = block.smash()
        elif action == PAINT:
            move_successful = block.paint(target_color)
        elif action == COMBINE:
            move_successful = block.combine()
        elif action == PASS:
            move_successful = True
        return move_successful

    def test_create_player(self) -> None:
        players1 = create_players(1, 0, [i for i in range(3)])
        self.assert_player_equal(players1, 1, 0, [i for i in range(3)])
        players2 = create_players(1, 3, [])
        self.assert_player_equal(players2, 1, 3, [])
        players3 = create_players(0, 0, [i for i in range(4)])
        self.assert_player_equal(players3, 0, 0, [i for i in range(4)])

    def assert_player_equal(self, players: List[Player], num_humans: int,
                            num_random: int, smart_players: List[int]) -> None:
        for player_i in range(len(players)):
            self.assertEqual(players[player_i].id, player_i,
                             "id should start at 0 and add in sequence")
        for player in players[: num_humans]:
            self.assertTrue(isinstance(player, HumanPlayer),
                            "should start with human players")
        for player in players[num_humans: num_humans + num_random]:
            self.assertTrue(isinstance(player, RandomPlayer))
        for player in players[num_humans + num_random:
        num_random + num_humans + len(smart_players)]:
            self.assertTrue(isinstance(player, SmartPlayer))

    def test_random_player_generate_move_internal(self):
        broad = self.one_internal
        target_color = (50, 50, 50)
        goal = BlobGoal(target_color)
        rplayer1 = RandomPlayer(0, goal)
        rplayer1._proceed = True
        move = rplayer1.generate_move(broad)
        self.assertTrue(self.do_action(move[2], (move[0], move[1]), target_color),
                        "the move should be successful")

    def test_random_player_generate_move_level(self):
        broad = self.one_level
        target_color = (10, 10, 10)
        goal = BlobGoal(target_color)
        rplayer1 = RandomPlayer(0, goal)
        rplayer1._proceed = True
        move = rplayer1.generate_move(broad)
        self.assertTrue(
            self.do_action(move[2], (move[0], move[1]), target_color),
            "the move should be successful")

    @patch("block.Block.paint", return_value=False)
    def test_smart_player_do_pass(self, mock_paint):
        """
        (0, 0, (30， 30， 30))      (5, 0， (20, 20, 20))
                        ___________________________
                        |            |             |
                        |            |             |
                        |            |             |
            (0, 5, (40, 40, 40))           (5, 5, (50, 50, 50))
                        |____________|____________ |
                        |            |             |
                        |            |             |
                        |            |             |
                        |____________|_____________|
        We mock paint to return False.  You can pretend that in this case calling paint is an invalid move even though
        technically it is a valid move.  So that you have 4 valid moves that are rotating and swaping.  But none of them
        can increase the score so you have to return pass
        """
        board = self.one_level
        target_color = (10, 10, 10)
        goal = BlobGoal(target_color)
        for i in range(1, 5):
            splayer1 = SmartPlayer(0, goal, i)
            splayer1._proceed = True
            move = splayer1.generate_move(board)
            self.assertEqual('pass', move[0], "There is no better move on"
                                              " this broad")

    def test_smart_player_paint(self):
        """
            ____________
            |           |
            |           |
            |___________|
        colour:(10, 10, 10)
        """
        board = Block((0, 0), 10, (10, 10, 10), 0, 0)
        target_color = (100, 100, 100)
        goal = BlobGoal(target_color)
        player = self.create_player(0, goal, 1)
        move = player.generate_move(board)
        self.assertEqual('paint', move[0], "The only valid move for a leaf is paint")
        self.assertEqual(None, move[1])

    def test_smart_player_paint_2(self):
        """
        (0, 0, (30， 30， 30))      (5, 0， (20, 20, 20))
                        ___________________________
                        |            |             |
                        |            |             |
                        |            |             |
            (0, 5, (40, 40, 40))           (5, 5, (50, 50, 50))
                        |____________|____________ |
                        |            |             |
                        |            |             |
                        |            |             |
                        |____________|_____________|
        """
        board = self.one_level
        target_color = (100, 100, 100)
        goal = PerimeterGoal(target_color)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(board)
        self.assertEqual('paint', move[0])

    @patch("block.Block.paint", return_value=False)
    @patch("block.Block.smash", return_value=False)
    @patch("block.Block.swap", return_value=False)
    def test_smart_player_rotate_1(self, mock_paint, mock_smash, mock_swap):
        """
            B____________A_____________
            |/ / / / / / |             |
            |/ / / / / / |             |
            |/ / / / / / |             |
            D/_/_/C_/_/__G_____________|
            |     |/ / / |             |
            E_____F/_/_/_|             |
            |     |/ / / |             |
            |_____|/_/_/_|_____________|
        Before:
            A:(50, 0, (10, 10, 10))
            B:(0, 0, (20, 20, 20))
            C:(25, 50, (20, 20, 20))
            D:(0, 50, (30, 30, 30))
            E:(0, 75, (30, 30, 30))
            F:(25, 75, (20, 20, 20))
            G:(50, 50, (40, 40, 40))
        Here we are using blob goal and you can pretend that paint, smash and swap are invalid moves because we set
        them to return False for testing purpose
        You can regard that in this case rotate is the only valid move
        """
        temp = Block((0, 0), 100, None, 0, 2)
        self.set_children(temp, [(i, i, i) for i in range(10, 50, 10)])
        self.set_children(temp.children[2], [(i, i, i) for i in range(20, 60, 10)])
        temp.children[2].children[1].colour = (30, 30, 30)
        temp.children[2].children[2].colour = (30, 30, 30)
        temp.children[2].children[3].colour = (20, 20, 20)
        target_colour = (20, 20, 20)
        goal = PerimeterGoal(target_colour)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(temp)
        self.assertEqual('rotate', move[0])
        self.assertEqual(1, move[1])

    @patch("block.Block.paint", return_value=False)
    @patch("block.Block.smash", return_value=False)
    @patch("block.Block.swap", return_value=False)
    def test_smart_player_rotate_2(self, mock_paint, mock_smash, mock_swap):
        """
            C______B______A_____________
            |      | / / |/ / / / / / /|
            D______E/_/_/|/ / / / / / /|
            |      | / / |/ / / / / / /|
            F______|/_/_/G_____________|
            |            |             |
            |            |             |
            |            |             |
            |____________|_____________|
        Before:
            A:(50, 0, (10, 10, 10))
            B:(25, 0, (10, 10, 10))
            C:(0, 0, (20, 20, 20))
            D:(0, 25, (20, 20, 20))
            E:(25, 25, (10, 10, 10))
            F:(0, 50, (30, 30, 30))
            G:(50, 50, (40, 40, 40))
        Here we are using Perimeter goal and you can pretend the paint, smash and swap are invalid moves because we set
        them to return False for testing purpose
        You can regard that in this case rotate is the only valid move
        """
        temp = Block((0, 0), 100, None, 0, 2)
        self.set_children(temp, [(i, i, i) for i in range(10, 50, 10)])
        self.set_children(temp.children[1], [(i, i, i) for i in range(10, 50, 10)])
        temp.children[1].children[1].colour = (20, 20, 20)
        temp.children[1].children[2].colour = (20, 20, 20)
        temp.children[1].children[3].colour = (10, 10, 10)
        target_colour = (10, 10, 10)
        goal = PerimeterGoal(target_colour)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(temp)
        self.assertEqual('rotate', move[0])
        self.assertEqual(3, move[1])

    @patch("block.Block.paint", return_value=False)
    @patch("block.Block.smash", return_value=False)
    @patch("block.Block.rotate", return_value=False)
    def test_smart_player_swap_1(self, mock_paint, mock_smash, mock_rotate):
        """
            B____________A_____________
            |/ / / / / / |             |
            |/ / / / / / |             |
            |/ / / / / / |             |
            D/_/_/C_/_/__G_____________|
            |     |/ / / |             |
            E_____F/_/_/_|             |
            |     |/ / / |             |
            |_____|/_/_/_|_____________|
        Before:
            A:(50, 0, (10, 10, 10))
            B:(0, 0, (20, 20, 20))
            C:(25, 50, (20, 20, 20))
            D:(0, 50, (30, 30, 30))
            E:(0, 75, (30, 30, 30))
            F:(25, 75, (20, 20, 20))
            G:(50, 50, (40, 40, 40))
        Here we are using Perimeter goal and you can pretend that paint, smash and rotate are invalid moves because we set
        them to return False for testing purpose
        You can regard that in this case swap is the only valid move
        """
        temp = Block((0, 0), 100, None, 0, 2)
        self.set_children(temp, [(i, i, i) for i in range(10, 50, 10)])
        self.set_children(temp.children[2], [(i, i, i) for i in range(20, 60, 10)])
        temp.children[2].children[1].colour = (30, 30, 30)
        temp.children[2].children[2].colour = (30, 30, 30)
        temp.children[2].children[3].colour = (20, 20, 20)
        target_colour = (20, 20, 20)
        goal = PerimeterGoal(target_colour)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(temp)
        self.assertEqual('swap', move[0])
        self.assertEqual(0, move[1])

    @patch("block.Block.paint", return_value=False)
    @patch("block.Block.smash", return_value=False)
    @patch("block.Block.rotate", return_value=False)
    def test_smart_player_swap_2(self, mock_paint, mock_smash, mock_rotate):
        """
            C______B______A_____________
            |      |     |/ / / / / / /|
            D______E_____|/ / / / / / /|
            |/ / / | / / |/ / / / / / /|
            F/_/_/_|/_/_/G_____________|
            |            |             |
            |            |             |
            |            |             |
            |____________|_____________|
        Before:
            A:(50, 0, (10, 10, 10))
            B:(25, 0, (20, 20, 20))
            C:(0, 0, (20, 20, 20))
            D:(0, 25, (10, 10, 10))
            E:(25, 25, (10, 10, 10))
            F:(0, 50, (30, 30, 30))
            G:(50, 50, (40, 40, 40))
        Here we are using Perimeter goal and you can pretend the paint, smash and rotate are invalid moves because we set
        them to return False for testing purpose
        You can regard that in this case swap is the only valid move
        """
        temp = Block((0, 0), 100, None, 0, 2)
        self.set_children(temp, [(i, i, i) for i in range(10, 50, 10)])
        self.set_children(temp.children[1], [(i, i, i) for i in range(10, 50, 10)])
        temp.children[1].children[0].colour = (20, 20, 20)
        temp.children[1].children[1].colour = (20, 20, 20)
        temp.children[1].children[2].colour = (10, 10, 10)
        temp.children[1].children[3].colour = (10, 10, 10)
        target_colour = (10, 10, 10)
        goal = PerimeterGoal(target_colour)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(temp)
        self.assertEqual('swap', move[0])
        self.assertEqual(1, move[1])

    @patch("block.Block.rotate", return_value=False)
    @patch("block.Block.swap", return_value=False)
    def test_smart_player_combine(self, mock_rotate, mock_swap):
        """
            (0, 0, (30， 30， 30))      (5, 0， (20, 20, 20))
                        ___________________________
                        |            |             |
                        |            |             |
                        |            |             |
            (0, 5, (20, 20, 20))           (5, 5, (50, 50, 50))
                        |____________|____________ |
                        |            |             |
                        |            |             |
                        |            |             |
                        |____________|_____________|

        Here we are using Blob goal and you can regard that in this case rotate and swap are invalid moves
        Only paint and combine are valid moves
        To maximize the score you have to pick the combine
        """
        board = self.one_level
        board.children[2].colour = (20, 20, 20)
        target_color = (20, 20, 20)
        goal = BlobGoal(target_color)
        player = self.create_player(0, goal, 800)
        move = player.generate_move(board)
        self.assertEqual('combine', move[0])
        self.assertEqual(None, move[1])


if __name__ == "__main__":
    unittest.main(exit=False)
