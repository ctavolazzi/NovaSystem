import unittest
from unittest.mock import patch, MagicMock
from ai_manager import AIManager

class TestAIManager(unittest.TestCase):

    def setUp(self):
        self.ai_manager = AIManager()

    @patch('ollama.chat')
    def test_generate_story_node(self, mock_chat):
        mock_chat.return_value = {
            "message": {
                "content": '{"title": "Test Node", "text": "Test content", "choices": ["Choice 1", "Choice 2"], "characters": [{"name": "Character 1", "description": "Description 1"}], "items": [{"name": "Item 1", "description": "Description 1"}], "loot": [{"name": "Loot 1", "description": "Description 1"}]}'
            }
        }

        context = {
            "player_name": "Test Player",
            "player_class": "Warrior",
            "current_situation": "In a forest",
            "story_arc": {"current_phase": "introduction", "overall_story": "An epic quest"}
        }

        result = self.ai_manager.generate_story_node(context)

        self.assertEqual(result["title"], "Test Node")
        self.assertEqual(result["text"], "Test content")
        self.assertEqual(len(result["choices"]), 2)
        self.assertEqual(len(result["characters"]), 1)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(len(result["loot"]), 1)

    def test_caching_mechanism(self):
        # Mock the ollama.chat to return a unique response each time
        with patch('ollama.chat', side_effect=[
            {"message": {"content": '{"title": "Node 1"}'}},
            {"message": {"content": '{"title": "Node 2"}'}},
        ]):
            context = {"key": "value"}
            
            # First call should generate a new response
            result1 = self.ai_manager.generate_story_node(context)
            self.assertEqual(result1["title"], "Node 1")

            # Second call with the same context should return the cached result
            result2 = self.ai_manager.generate_story_node(context)
            self.assertEqual(result2["title"], "Node 1")  # Should be the same as result1

    @patch('ollama.chat')
    def test_error_handling(self, mock_chat):
        mock_chat.side_effect = Exception("API Error")

        result = self.ai_manager.generate_story_node({})

        self.assertEqual(result["title"], "Unexpected Turn")
        self.assertTrue("The path ahead is unclear" in result["text"])

if __name__ == '__main__':
    unittest.main()