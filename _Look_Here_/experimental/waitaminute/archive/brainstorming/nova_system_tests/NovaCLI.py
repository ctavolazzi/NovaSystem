from NovaChatBot import NovaChatBot
from NovaSystem.Modules.Config.ConfigManager import NovaConfigManager
from NovaSystem.Modules.Helpers.NovaHelper import stc

class NovaCLI:
    def __init__(self, config=None):
        self.config_manager = NovaConfigManager(config)
        self.cli_chatbot = NovaChatBot(config)
        self.openai_api_key = self.config_manager.get_openai_api_key()

    def initialize_chatbot(self):
        config = {
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant named Nova.",
            "api_key": self.openai_api_key,
            "engine": "davinci",
            "temperature": 0.9,
            "max_tokens": 150,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.6,
            "stop": ["\n", " Human:", " Nova:"]
        }
        self.cli_chatbot.apply_config()

    def run(self):
        stc("Nova System Activated...")
        stc('"Hello, world!"')
        stc('Type "exit" or "q" to quit.\n')

        while True:
            user_input = input("> ")
            if user_input.lower() in ["exit", "q"]:
                break
            # While True, perform the actions of a CLI chatbot.

            # 1) Interpret user input
            # 2) Send user input to Nova
            # 3) Receive response from Nova
            # 4) Display response to user

            self.set_up_chatbot()
            self.cli_chatbot.fetch_and_stream_single_turn(user_input)


            # response = self.cli_chatbot.fetch_openai_chat_response(user_input)
            # self.cli_chatbot.stream_deltas_to_console(response)

    def test(self):
        stc(f'Testing NovaCLI...')

if __name__ == "__main__":
    nova_cli = NovaCLI()
    nova_cli.test()
    nova_cli.run()