import unittest
from unittest.mock import patch, MagicMock
from game import Game
from character import Character
from story_node import StoryNode

class TestStoryGeneration(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.player_character = Character(1, 'Test Player', 'A test character', {'class': 'Warrior'})
        self.game.game_id = 1

    @patch('game.AIManager.generate_story_node')
    def test_generate_story_node(self, mock_generate_node):
        mock_generate_node.return_value = {
            'title': 'Test Node',
            'text': 'This is a test node',
            'choices': ['Choice 1', 'Choice 2'],
            'characters': [{'name': 'Test Character', 'description': 'A test character'}],
            'items': [],
            'loot': []
        }

        self.game._generate_story_node()

        self.assertIsNotNone(self.game.current_node)
        self.assertEqual(self.game.current_node.title, 'Test Node')
        self.assertEqual(len(self.game.current_node.choices), 2)
        self.assertEqual(len(self.game.current_node.characters), 1)

    @patch('game.Game._generate_story_node')
    def test_handle_choice(self, mock_generate_node):
        self.game.current_node = StoryNode(1, 'Test Node', 'Test text', ['Choice 1', 'Choice 2'], [], [], [])
        self.game._handle_choice(0)
        mock_generate_node.assert_called_once()

if __name__ == '__main__':
    unittest.main()