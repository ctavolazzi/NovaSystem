import unittest
from unittest.mock import MagicMock
from character import Character
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCharacter(unittest.TestCase):
    def setUp(self):
        self.character = Character(1, 'Test Character', 'A test character', {'class': 'Warrior', 'strength': 10})

    def test_character_initialization(self):
        self.assertEqual(self.character.name, 'Test Character')
        self.assertEqual(self.character.attributes['class'], 'Warrior')
        self.assertEqual(self.character.attributes['strength'], 10)

    def test_gain_experience(self):
        initial_level = self.character.level
        self.character.gain_experience(100)
        self.assertEqual(self.character.level, initial_level + 1)

    def test_equip_item(self):
        item = MagicMock()
        item.name = 'Test Item'
        item.effect = {'strength': 5}
        self.character.equip_item(item)
        self.assertIn(item, self.character.equipped_items)
        self.assertEqual(self.character.attributes['strength'], 15)

if __name__ == '__main__':
    unittest.main()