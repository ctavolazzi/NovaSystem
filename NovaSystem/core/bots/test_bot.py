import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from Bot_01 import Bot, ChatBot, Port
import logging
import os
import asyncio
from datetime import datetime

class TestBot(unittest.TestCase):
    def test_bot_initialization(self):
        bot = Bot()
        self.assertIsInstance(bot.id, str)
        self.assertIsInstance(bot.name, str)
        self.assertIsInstance(bot.logger, logging.Logger)
        self.assertIsInstance(bot.port, Port)

    def test_bot_say(self):
        bot = Bot()
        message = "Hello, world!"
        with patch.object(bot.port, 'send') as mock_send:
            returned_message = bot.say(message)
            mock_send.assert_called_once_with(message)
            self.assertEqual(returned_message, message)

    def test_bot_say_invalid_data(self):
        bot = Bot()
        with self.assertRaises(TypeError):
            bot.say(123)  # Non-string data

    def test_bot_listen(self):
        bot = Bot()
        input_data = "Test input"
        with patch.object(bot.port, 'receive', return_value=input_data):
            success, data = bot.listen()
            self.assertTrue(success)
            self.assertEqual(data, input_data)

    def test_bot_listen_error(self):
        bot = Bot()
        with patch.object(bot.port, 'receive', side_effect=Exception("Test error")):
            success, data = bot.listen()
            self.assertFalse(success)
            self.assertIsNone(data)

    def test_generate_random_name(self):
        bot = Bot()
        name = bot._generate_random_name()
        self.assertEqual(len(name), 8)
        self.assertTrue(name.isalnum())

    def test_logger_initialization(self):
        bot = Bot()
        self.assertEqual(bot.logger.level, logging.INFO)
        self.assertIn(bot.name, bot.logger.name)

    def test_port_initialization(self):
        bot = Bot()
        port = bot.port
        self.assertIsInstance(port.port_id, str)

    def test_port_send_invalid_data(self):
        bot = Bot()
        with self.assertRaises(TypeError):
            bot.port.send(123)  # Non-string data

    def test_port_receive(self):
        bot = Bot()
        with patch.object(bot.port, 'receive', return_value="Test data"):
            data = bot.port.receive()
            self.assertEqual(data, "Test data")

class TestChatBot(unittest.IsolatedAsyncioTestCase):
    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_initialization(self, mock_openai):
        chatbot = ChatBot()
        self.assertIsInstance(chatbot, ChatBot)
        self.assertEqual(chatbot.api_key, 'mocked_api_key')
        mock_openai.assert_called_once_with(api_key='mocked_api_key')

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    async def test_chatbot_base_action_generate_report(self, mock_print, mock_file, mock_openai):
        chatbot = ChatBot()
        await chatbot.generate_report()
        mock_print.assert_called_with(f"Bot ID: {chatbot.id}\nBot Name: {chatbot.name}\n")
        mock_file.assert_called_with(os.path.join(chatbot.report_directory, 'report.txt'), 'w')

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_generate_response(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_stream = MagicMock()
        mock_stream.__aiter__.return_value = iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test response"))])
        ])
        mock_client.chat.completions.create.return_value = mock_stream

        chatbot = ChatBot()
        response = await chatbot.generate_response("Hello, bot!")
        self.assertIn('Response to: Hello, bot!', response)
        self.assertIn('Test response', response)

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_is_content_allowed(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.moderations.create.return_value = MagicMock(results=[MagicMock(flagged=False)])

        chatbot = ChatBot()
        result = await chatbot._is_content_allowed("Safe content")
        self.assertTrue(result)

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_is_content_not_allowed(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.moderations.create.return_value = MagicMock(results=[MagicMock(flagged=True)])

        chatbot = ChatBot()
        result = await chatbot._is_content_allowed("Unsafe content")
        self.assertFalse(result)

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_save_interaction(self, mock_openai):
        with patch('Bot_01.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.isoformat.return_value = '2023-01-01T00:00:00'
            mock_datetime.now.return_value = mock_now

            chatbot = ChatBot()
            conversation_id = 'test_convo'
            chatbot.save_interaction(conversation_id, 'user', 'Hello')
            interaction = chatbot.conversations[conversation_id][0]
            self.assertEqual(interaction['timestamp'], '2023-01-01T00:00:00')

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_generate_response_saves_interactions(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_stream = MagicMock()
        mock_stream.__aiter__.return_value = iter([
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test response"))])
        ])
        mock_client.chat.completions.create.return_value = mock_stream

        chatbot = ChatBot()
        with patch.object(chatbot, 'save_interaction') as mock_save:
            response = await chatbot.generate_response("Test prompt", 'test_convo')
            self.assertIn('Response to: Test prompt', response)
            mock_save.assert_has_calls([
                call('test_convo', 'user', 'Test prompt'),
                call('test_convo', 'assistant', 'Test response')
            ], any_order=False)

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_get_conversation_nonexistent(self, mock_openai):
        chatbot = ChatBot()
        conversation = chatbot.get_conversation('nonexistent_convo')
        self.assertEqual(conversation, [])

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    @patch('builtins.open', new_callable=mock_open)
    async def test_save_conversations_creates_file(self, mock_file, mock_openai):
        chatbot = ChatBot()
        chatbot.conversations = {"conversation_id": []}
        chatbot.save_conversations()
        mock_file.assert_called_with(chatbot.conversation_file, 'w')

    @patch('Bot_01.OpenAI')  # Correctly patch 'Bot_01.OpenAI'
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'mocked_api_key'})
    async def test_chatbot_base_action_generate_report_async(self, mock_openai):
        with patch('builtins.print') as mock_print, patch('builtins.open', new_callable=mock_open) as mock_file:
            chatbot = ChatBot()
            await chatbot.generate_report()
            mock_print.assert_called_with(f"Bot ID: {chatbot.id}\nBot Name: {chatbot.name}\n")
            mock_file.assert_called_with(os.path.join(chatbot.report_directory, 'report.txt'), 'w')

if __name__ == '__main__':
    unittest.main()