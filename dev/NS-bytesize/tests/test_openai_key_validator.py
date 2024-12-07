# Standard library
import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Local imports
from utils.openai_key_validator import OpenAIKeyValidator

class TestOpenAIKeyValidator(unittest.TestCase):
    """Test cases for OpenAIKeyValidator."""

    def setUp(self):
        """Set up test cases."""
        # Save original environment
        self.original_key = os.environ.get('OPENAI_API_KEY')
        # Create a mock env path
        self.mock_env_path = MagicMock(spec=Path)
        self.mock_env_path.exists.return_value = False

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment
        if self.original_key:
            os.environ['OPENAI_API_KEY'] = self.original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

    def test_valid_key(self):
        """Test validator with a valid API key."""
        test_key = "sk-test123validkey456"
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            validator = OpenAIKeyValidator(env_path=self.mock_env_path, search_tree=False)
            self.assertTrue(validator.is_valid)
            self.assertEqual(validator.key, test_key)

    def test_invalid_key_format(self):
        """Test validator with invalid key format."""
        test_key = "invalid-key-format"
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            validator = OpenAIKeyValidator(env_path=self.mock_env_path, search_tree=False)
            self.assertFalse(validator.is_valid)
            with self.assertRaises(ValueError):
                _ = validator.key

    def test_placeholder_key(self):
        """Test validator with placeholder key."""
        test_key = "your-actual-api-key"
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            validator = OpenAIKeyValidator(env_path=self.mock_env_path, search_tree=False)
            self.assertFalse(validator.is_valid)
            with self.assertRaises(ValueError):
                _ = validator.key

    def test_missing_key(self):
        """Test validator with no API key."""
        with patch.dict(os.environ, {}, clear=True):
            validator = OpenAIKeyValidator(env_path=self.mock_env_path, search_tree=False)
            self.assertFalse(validator.is_valid)
            with self.assertRaises(ValueError):
                _ = validator.key

    def test_env_file_loading(self):
        """Test .env file loading functionality."""
        test_key = "sk-test123validkey456"
        mock_env_path = MagicMock(spec=Path)
        mock_env_path.exists.return_value = True

        with patch('utils.openai_key_validator.load_dotenv', return_value=True) as mock_load_dotenv:
            with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
                validator = OpenAIKeyValidator(env_path=mock_env_path, search_tree=False)

                # Verify load_dotenv was called with the correct arguments
                mock_load_dotenv.assert_called_once_with(mock_env_path, override=True)
                self.assertTrue(validator.is_valid)
                self.assertEqual(validator.key, test_key)

if __name__ == '__main__':
    unittest.main(verbosity=2)
