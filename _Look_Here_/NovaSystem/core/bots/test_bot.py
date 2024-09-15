import unittest
from unittest.mock import patch, AsyncMock
import os
import uuid
import shutil
import asyncio

# Assuming the Bot, Port, and ChatBot classes are defined in the same module or accessible scope.

class TestBot(unittest.TestCase):
    def setUp(self):
        """
        Set up the testing environment before each test case.
        """
        # Set a dummy OpenAI API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        self.log_dir = 'test_logs'
        # Initialize the ChatBot instance
        self.bot = ChatBot(log_dir=self.log_dir)

    def tearDown(self):
        """
        Clean up after each test case.
        """
        # Remove the dummy API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        # Remove test logs and memory files
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)

    def test_bot_initialization(self):
        """
        Test that the bot initializes correctly.
        """
        self.assertIsInstance(self.bot.id, uuid.UUID)
        self.assertIsInstance(self.bot.name, str)
        self.assertIsInstance(self.bot.port, Port)
        self.assertEqual(self.bot.log_dir, self.log_dir)
        self.assertTrue(os.path.exists(self.bot.log_dir))
        self.assertTrue(os.path.exists(self.bot.offboard_memory_file))

    def test_port_unique_id(self):
        """
        Test that the port has a unique port_id.
        """
        self.assertIsInstance(self.bot.port.port_id, uuid.UUID)
        # Create another bot and ensure the port IDs are unique
        another_bot = ChatBot(log_dir=self.log_dir)
        self.assertNotEqual(self.bot.port.port_id, another_bot.port.port_id)

    def test_say_method(self):
        """
        Test that the say method uses the port's send method.
        """
        test_data = "Hello, world!"
        with patch.object(self.bot.port, 'send') as mock_send:
            self.bot.say(test_data)
            mock_send.assert_called_with(test_data)

    def test_listen_method(self):
        """
        Test that the listen method uses the port's receive method.
        """
        test_data = "Test input"
        with patch.object(self.bot.port, 'receive', return_value=test_data) as mock_receive:
            success, data = self.bot.listen()
            mock_receive.assert_called()
            self.assertTrue(success)
            self.assertEqual(data, test_data)

    def test_write_and_read_offboard_memory(self):
        """
        Test writing to and reading from offboard memory.
        """
        test_data = "Test memory data"
        self.bot.write_offboard_memory(test_data)
        data = self.bot.read_offboard_memory()
        self.assertIn(test_data, data)

    @patch('openai.Completion.acreate')
    @patch('openai.Moderation.acreate')
    def test_generate_response(self, mock_moderation_acreate, mock_completion_acreate):
        """
        Test the generate_response method with allowed content.
        """
        # Mock the moderation API to allow the content
        async def mock_moderation(*args, **kwargs):
            return {'results': [{'flagged': False}]}
        mock_moderation_acreate.side_effect = mock_moderation

        # Mock the completion API to return a test response
        async def mock_completion(*args, **kwargs):
            return {'choices': [{'text': 'This is a test response.'}]}
        mock_completion_acreate.side_effect = mock_completion

        # Run the generate_response method asynchronously
        response = asyncio.run(self.bot.generate_response("Test prompt"))
        self.assertEqual(response, 'This is a test response.')
        # Ensure moderation was called for both prompt and response
        self.assertEqual(mock_moderation_acreate.call_count, 2)
        mock_completion_acreate.assert_called_once()

    @patch('openai.Completion.acreate')
    @patch('openai.Moderation.acreate')
    def test_generate_response_disallowed_content(self, mock_moderation_acreate, mock_completion_acreate):
        """
        Test the generate_response method when content is disallowed.
        """
        # Mock the moderation API to flag the content
        async def mock_moderation_flagged(*args, **kwargs):
            return {'results': [{'flagged': True}]}
        mock_moderation_acreate.side_effect = mock_moderation_flagged

        # Run the generate_response method asynchronously
        response = asyncio.run(self.bot.generate_response("Disallowed content"))
        self.assertIsNone(response)
        # Ensure that the completion API was not called
        mock_completion_acreate.assert_not_called()
        # Ensure moderation was called once
        mock_moderation_acreate.assert_called_once()

    def test_missing_api_key(self):
        """
        Test that the bot raises a ValueError when the API key is missing.
        """
        del os.environ['OPENAI_API_KEY']
        with self.assertRaises(ValueError):
            bot = ChatBot(log_dir=self.log_dir)

    def test_bot_communicates_only_through_its_port(self):
        """
        Test that the bot communicates only through its own port.
        """
        external_port = Port(self.bot)
        with patch.object(external_port, 'send') as mock_send, \
             patch.object(external_port, 'receive', return_value="External input"):
            self.bot.port = external_port  # Replace the bot's port with an external port
            success, data = self.bot.listen()
            self.assertTrue(success)
            self.assertEqual(data, "External input")
            self.bot.say("Response")
            mock_send.assert_called_with("Response")

    def test_base_action(self):
        """
        Test the base_action method of ChatBot.
        """
        with patch.object(self.bot, 'listen', return_value=(True, "Hello")), \
             patch.object(self.bot, 'generate_response', return_value=asyncio.Future()) as mock_generate_response, \
             patch.object(self.bot, 'say') as mock_say:
            mock_generate_response.return_value.set_result("Hi there!")
            self.bot.base_action()
            mock_say.assert_called_with("Hi there!")

    def test_content_moderation_error(self):
        """
        Test handling when the content moderation API encounters an error.
        """
        with patch('openai.Moderation.acreate', side_effect=openai.error.OpenAIError("API Error")):
            response = asyncio.run(self.bot._is_content_allowed("Test content"))
            self.assertFalse(response)

    @patch.object(Port, 'receive', return_value="Tell me a joke.")
    @patch.object(Port, 'send')
    def test_full_communication_cycle(self, mock_send, mock_receive):
        """
        Test the bot's full communication cycle through its port.
        """
        # Mock the OpenAI API calls
        with patch('openai.Completion.acreate') as mock_completion_acreate, \
             patch('openai.Moderation.acreate') as mock_moderation_acreate:

            async def mock_moderation(*args, **kwargs):
                return {'results': [{'flagged': False}]}

            async def mock_completion(*args, **kwargs):
                return {'choices': [{'text': 'Why did the chicken cross the road? To get to the other side!'}]}

            mock_moderation_acreate.side_effect = mock_moderation
            mock_completion_acreate.side_effect = mock_completion

            self.bot.base_action()

            # Check that the bot received data through its port
            mock_receive.assert_called_once()
            # Check that the bot sent data through its port
            mock_send.assert_called_once_with('Why did the chicken cross the road? To get to the other side!')

    def test_offboard_memory_file_creation(self):
        """
        Test that the offboard memory file is created upon initialization.
        """
        self.assertTrue(os.path.isfile(self.bot.offboard_memory_file))

    def test_port_send_receive_logging(self):
        """
        Test that port send and receive actions are logged.
        """
        with patch.object(self.bot.logger, 'log') as mock_log:
            test_data = "Test data"
            self.bot.port.send(test_data)
            self.bot.port.receive()
            # Check that log was called for send and receive
            self.assertTrue(any("sending data" in call.args[0] for call in mock_log.call_args_list))
            self.assertTrue(any("received data" in call.args[0] for call in mock_log.call_args_list))

if __name__ == '__main__':
    unittest.main()
