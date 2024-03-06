import unittest
from unittest.mock import patch
from memento import Memento, ConcreteMemento, Originator, Caretaker

class TestMementoPattern(unittest.TestCase):
    def setUp(self):
        self.originator = Originator("Initial State")
        self.caretaker = Caretaker(self.originator)

    def test_memento_creation(self):
        """Test the creation of a memento and its properties."""
        memento = self.originator.save()
        self.assertIsInstance(memento, ConcreteMemento)
        self.assertTrue(memento.get_name().startswith("20"))  # Assuming current year
        self.assertTrue(memento.get_date().startswith("20"))  # Assuming current year

    def test_state_restoration(self):
        """Test the restoration of the state in the originator from a memento."""
        self.originator._state = "New State"
        memento = self.originator.save()
        self.originator._state = "Another State"
        self.originator.restore(memento)
        self.assertEqual(self.originator._state, "New State")

    def test_caretaker_memento_management(self):
        """Test the caretaker's ability to store and retrieve mementos."""
        self.caretaker.backup()
        self.caretaker.backup()
        self.assertEqual(len(self.caretaker._mementos), 2)

    def test_caretaker_undo_functionality(self):
        """Test the caretaker's undo functionality."""
        self.originator._state = "State A"
        self.caretaker.backup()
        self.originator._state = "State B"
        self.caretaker.backup()
        self.caretaker.undo()
        self.assertEqual(self.originator._state, "State A")

def main():
    unittest.main()

if __name__ == '__main__':
    main()
