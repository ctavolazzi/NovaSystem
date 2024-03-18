from NovaChatBot import NovaChatBot
from NovaConfigManager import ConfigManager
from NovaHelper import Helper

# Eventually these will all be in one class: NovaSystem

class NovaCLI:
    def __init__(self, config=None):
        self.sockets = []
        self.config_manager = ConfigManager(config)
        self.cli_chatbot = NovaChatBot(config)
        self.helper = Helper()

    def run(self):
        print("Nova System Activated...")
        print('"Hello, world!"')
        print('Type "exit" or "q" to quit.\n')

        while True:
            user_input = input("> ")
            if user_input in ["exit", "q"]:
                break
            response = self.cli_chatbot.fetch_and_stream_single_turn(user_input)
            self.output_function(response)

    def output_function(self, text):
        print(text)

if __name__ == "__main__":
    nova_cli = NovaCLI()
    nova_cli.run()