import unittest
import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from game import AIManager

class TestAIManager(unittest.TestCase):

    def test_properly_formatted_json_response(self):
        ai_manager = AIManager()
        context = {
            "player_name": "TestHero",
            "player_class": "Warrior",
            "current_situation": "Starting point",
            "story_arc": {
                "current_phase": "introduction",
                "overall_story": "Test story"
            }
        }

        story_node_data = ai_manager.generate_story_node(context)
        print("Generated Story Node Data (Properly Formatted JSON):")
        print(json.dumps(story_node_data, indent=2))

        self.assertIsNotNone(story_node_data)
        self.assertIn("title", story_node_data)
        self.assertIn("text", story_node_data)
        self.assertIn("choices", story_node_data)
        self.assertIn("characters", story_node_data)
        self.assertIn("items", story_node_data)
        self.assertIn("loot", story_node_data)

    def test_response_with_additional_text(self):
        ai_manager = AIManager()
        context = {
            "player_name": "TestHero",
            "player_class": "Warrior",
            "current_situation": "Starting point",
            "story_arc": {
                "current_phase": "introduction",
                "overall_story": "Test story"
            }
        }

        story_node_data = ai_manager.generate_story_node(context)
        print("Generated Story Node Data (With Additional Text):")
        print(json.dumps(story_node_data, indent=2))

        self.assertIsNotNone(story_node_data)
        self.assertIn("title", story_node_data)
        self.assertIn("text", story_node_data)
        self.assertIn("choices", story_node_data)
        self.assertIn("characters", story_node_data)
        self.assertIn("items", story_node_data)
        self.assertIn("loot", story_node_data)

    def test_response_with_missing_fields(self):
        ai_manager = AIManager()
        context = {
            "player_name": "TestHero",
            "player_class": "Warrior",
            "current_situation": "Starting point",
            "story_arc": {
                "current_phase": "introduction",
                "overall_story": "Test story"
            }
        }

        story_node_data = ai_manager.generate_story_node(context)
        print("Generated Story Node Data (With Missing Fields):")
        print(json.dumps(story_node_data, indent=2))

        self.assertIsNotNone(story_node_data)
        self.assertIn("title", story_node_data)
        self.assertIn("text", story_node_data)
        self.assertIn("choices", story_node_data)
        self.assertIn("characters", story_node_data)
        self.assertIn("items", story_node_data)
        self.assertIn("loot", story_node_data)

    def test_invalid_json_response(self):
        ai_manager = AIManager()

        # Mocking the context for this specific test
        context = {
            "player_name": "TestHero",
            "player_class": "Warrior",
            "current_situation": "Invalid JSON Test",
            "story_arc": {
                "current_phase": "introduction",
                "overall_story": "Test story"
            }
        }

        # Simulate an invalid JSON response from the API
        try:
            response = ai_manager._response_adapter("Invalid JSON response")
        except Exception as e:
            response = ai_manager._generate_fallback_node()
        
        story_node_data = response
        print("Generated Story Node Data (Invalid JSON Response):")
        print(json.dumps(story_node_data, indent=2))

        self.assertIsNotNone(story_node_data)
        self.assertEqual(story_node_data["title"], "Unexpected Turn")
        self.assertEqual(story_node_data["text"], "The path ahead is unclear. What will you do?")
        self.assertEqual(story_node_data["choices"], ["Proceed carefully", "Find another way", "Rest and reconsider"])
        self.assertEqual(story_node_data["characters"], [])
        self.assertEqual(story_node_data["items"], [])
        self.assertEqual(story_node_data["loot"], [])

if __name__ == '__main__':
    unittest.main()
