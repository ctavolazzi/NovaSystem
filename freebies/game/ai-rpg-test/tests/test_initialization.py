import unittest
from unittest.mock import patch, MagicMock
import logging
from game import Game
from utils import ensure_game_directory

class TestGameInitialization(unittest.TestCase):

    @patch('game.SaveManager.generate_game_id')
    @patch('game.ensure_game_directory')
    @patch('game.Character.save_to_file')
    @patch('game.Game._generate_story_node')
    @patch('builtins.input', side_effect=['1', 'Test Player', '1'])
    def test_new_game_initialization(self, mock_input, mock_generate_story_node, mock_save_to_file, mock_ensure_directory, mock_generate_game_id):
        mock_generate_game_id.return_value = 1
        mock_ensure_directory.return_value = "Games/game_1"

        with self.assertLogs(level='INFO') as log:
            game = Game()
            game._new_game()

        self.assertIsNotNone(game.player_character)
        self.assertEqual(game.player_character.name, "Test Player")
        self.assertEqual(game.player_character.attributes['class'], "Village Hero")
        self.assertEqual(game.game_id, 1)
        
        mock_ensure_directory.assert_called_once_with(1)
        mock_save_to_file.assert_called_once()
        mock_generate_story_node.assert_called_once()

        # Check logs
        self.assertIn("INFO:root:Starting a new game", log.output)
        self.assertIn("INFO:root:Selected scenario: Village Hero", log.output)
        self.assertIn("INFO:root:Created player character: Test Player, ID: char_1", log.output)
        self.assertIn("INFO:root:Generated game ID: 1", log.output)
        self.assertIn("INFO:root:Calling ensure_game_directory with game_id: 1", log.output)
        self.assertIn("INFO:root:ensure_game_directory called successfully", log.output)
        self.assertIn("INFO:root:Player character saved to file", log.output)
        self.assertIn("INFO:root:Generated initial story node", log.output)

if __name__ == '__main__':
    unittest.main()