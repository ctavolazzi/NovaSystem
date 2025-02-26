# test_chatbot.py

import sys
import os

# Get the path to the parent directory of 'tests'
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)


import unittest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from bots.Bot_01 import ChatBot



class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or 'test_key'

    @patch('bots.Bot_01.OpenAI')
    def test_generate_response_with_mock(self, mock_openai):
        """Unit test for generate_response using mocked OpenAI client."""
        # Setup mock for OpenAI client
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance
        # Mock the asynchronous create method
        mock_client_instance.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        ))

        # Instantiate bot within patch context
        bot = ChatBot(api_key=self.api_key)

        # Run the asynchronous generate_response method
        response_content = asyncio.run(bot.generate_response('Hello'))

        self.assertIn('Test response', response_content)

        # Verify that the API was called with the correct parameters
        mock_client_instance.chat.completions.create.assert_awaited_with(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": 'Hello'}],
            stream=False,
        )

    @patch('bots.Bot_01.OpenAI')
    def test_is_content_allowed_with_mock(self, mock_openai):
        """Unit test for _is_content_allowed using mocked OpenAI client."""
        # Setup mock for OpenAI client
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance
        mock_client_instance.moderations.create = AsyncMock(return_value=MagicMock(
            results=[MagicMock(flagged=False)]
        ))

        # Instantiate bot within patch context
        bot = ChatBot(api_key=self.api_key)

        is_allowed = asyncio.run(bot._is_content_allowed('Safe content'))

        self.assertTrue(is_allowed)

    def test_save_and_load_conversations(self):
        """Test that conversations are saved and loaded correctly."""
        # Instantiate bot without mocking since we don't need OpenAI client here
        bot = ChatBot(api_key=self.api_key)
        # Specify a test-specific conversation file
        test_conversation_file = 'test_conversations.json'
        bot.conversation_file = test_conversation_file

        # Mock conversation data
        conversation_id = 'test_convo'
        bot.save_interaction(conversation_id, 'user', 'Hello')
        bot.save_interaction(conversation_id, 'assistant', 'Hi there!')

        # Reload the bot to simulate a restart
        new_bot = ChatBot(api_key=self.api_key, conversation_file=test_conversation_file)
        conversation = new_bot.get_conversation(conversation_id)

        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation[0]['content'], 'Hello')
        self.assertEqual(conversation[1]['content'], 'Hi there!')

        # Clean up test conversation file
        os.remove(test_conversation_file)

    # If you have other asynchronous tests, replace any use of get_event_loop
    # with asyncio.run() as shown above to avoid DeprecationWarnings

if __name__ == '__main__':
    unittest.main()