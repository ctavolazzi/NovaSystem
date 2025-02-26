import unittest
import sys
import os
from pathlib import Path

# Get the absolute path to the game directory
game_dir = Path(__file__).parent.parent.absolute()

# Add the game directory to the Python path
if str(game_dir) not in sys.path:
    sys.path.insert(0, str(game_dir))

# Import the test modules directly from the current package
from test_game_initialization import TestGameInitialization
from test_ai_manager import TestAIManager
from test_story_generation import TestStoryGeneration
from test_character import TestCharacter
from test_save_load import TestSaveLoad

if __name__ == '__main__':
    # Create a test suite combining all test cases
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGameInitialization))
    test_suite.addTest(unittest.makeSuite(TestAIManager))
    test_suite.addTest(unittest.makeSuite(TestStoryGeneration))
    test_suite.addTest(unittest.makeSuite(TestCharacter))
    test_suite.addTest(unittest.makeSuite(TestSaveLoad))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)