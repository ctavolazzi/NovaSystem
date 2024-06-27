import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_game_initialization import TestGameInitialization
from tests.test_ai_manager import TestAIManager
from tests.test_story_generation import TestStoryGeneration
from tests.test_character import TestCharacter
from tests.test_save_load import TestSaveLoad

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