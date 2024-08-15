import unittest
from unittest.mock import patch, MagicMock
from game import Game
from ai_manager import AIManager
from story_arc import StoryArc
from save_manager import SaveManager

class TestGameInitialization(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_initial_game_state(self):
        self.assertIsNone(self.game.player_character)
        self.assertIsNone(self.game.current_node)
        self.assertIsNone(self.game.story_tree)
        self.assertIsNone(self.game.game_id)
        self.assertIsInstance(self.game.ai_manager, AIManager)
        self.assertIsInstance(self.game.story_arc, StoryArc)
        self.assertIsInstance(self.game.save_manager, SaveManager)

    @patch('game.SaveManager.generate_game_id')
    @patch('game.ensure_game_directory')
    @patch('game.Character.save_to_file')
    @patch('game.Game._generate_story_node')
    @patch('builtins.input', side_effect=['1', 'Test Player', '1'])
    def test_new_game_initialization(self, mock_input, mock_generate_story_node, mock_save_to_file, mock_ensure_directory, mock_generate_game_id):
        mock_generate_game_id.return_value = 1
        mock_ensure_directory.return_value = "Games/game_1"

        with self.assertLogs(level='INFO') as log:
            self.game._new_game()

        self.assertIsNotNone(self.game.player_character)
        self.assertEqual(self.game.player_character.name, "Test Player")
        self.assertEqual(self.game.player_character.attributes['class'], "Village Hero")
        self.assertEqual(self.game.game_id, 1)
        
        mock_ensure_directory.assert_called_once_with(1)
        mock_save_to_file.assert_called_once()
        mock_generate_story_node.assert_called_once()

        self.assertIn("INFO:root:Starting a new game", log.output)
        self.assertIn("INFO:root:Selected scenario: Village Hero", log.output)
        self.assertIn("INFO:root:Created player character: Test Player, ID: char_1", log.output)
        self.assertIn("INFO:root:Generated game ID: 1", log.output)
        self.assertIn("INFO:root:Calling ensure_game_directory with game_id: 1", log.output)
        self.assertIn("INFO:root:ensure_game_directory called successfully", log.output)
        self.assertIn("INFO:root:Player character saved to file", log.output)
        self.assertIn("INFO:root:Generated initial story node", log.output)

    @patch('builtins.input', side_effect=['2', '1', 'y', '1'])  # Added an extra '1' for the player choice
    @patch('game.SaveManager.get_saved_games')
    @patch('game.SaveManager.load_game_state')
    @patch('game.StoryNode.load_from_file')
    @patch('game.Character.load_from_file')
    @patch('game.Game._generate_story_node')  # Add this line to mock _generate_story_node
    def test_load_saved_game(self, mock_generate_story_node, mock_character_load, mock_node_load, mock_load_state, mock_get_saved_games, mock_input):
        mock_get_saved_games.return_value = ['game_1']
        mock_load_state.return_value = {'current_node_id': 1, 'player_character_id': 1}
        mock_node_load.return_value = MagicMock(choices=['Choice 1', 'Choice 2'])
        mock_character_load.return_value = MagicMock()

        self.game.start()

        self.assertIsNotNone(self.game.current_node)
        self.assertIsNotNone(self.game.player_character)
        mock_load_state.assert_called_once()
        mock_node_load.assert_called_once()
        mock_character_load.assert_called_once()
        mock_generate_story_node.assert_called_once()  # Assert that _generate_story_node was called

if __name__ == '__main__':
    unittest.main()