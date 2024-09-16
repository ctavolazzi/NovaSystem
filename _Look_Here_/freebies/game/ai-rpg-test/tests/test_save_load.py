import unittest
from unittest.mock import patch, MagicMock

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from character import Character
from story_node import StoryNode

class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.player_character = Character(1, 'Test Player', 'A test character', {'class': 'Warrior'})
        self.game.game_id = 1
        self.game.current_node = StoryNode(1, 'Test Node', 'Test text', ['Choice 1', 'Choice 2'], [], [], [])

    @patch('game.SaveManager.save_game_state')
    def test_save_game_state(self, mock_save_game_state):
        self.game.save_manager.save_game_state(self.game.game_id, self.game.current_node.id, self.game.player_character)
        mock_save_game_state.assert_called_once_with(self.game.game_id, self.game.current_node.id, self.game.player_character)

    @patch('game.SaveManager.load_game_state')
    @patch('game.StoryNode.load_from_file')
    @patch('game.Character.load_from_file')
    def test_load_game_state(self, mock_character_load, mock_node_load, mock_load_state):
        mock_load_state.return_value = {'current_node_id': 1, 'player_character_id': 1}
        mock_node_load.return_value = MagicMock()
        mock_character_load.return_value = MagicMock()

        self.game._load_game_state()

        self.assertIsNotNone(self.game.current_node)
        self.assertIsNotNone(self.game.player_character)
        mock_load_state.assert_called_once()
        mock_node_load.assert_called_once()
        mock_character_load.assert_called_once()

if __name__ == '__main__':
    unittest.main()