from factory import BotFactory, ChatBot, DataAnalysisBot, ConcurrentBot

def test_bot_creation(factory):
    # Testing the creation of ChatBot
    print("Testing ChatBot Creation:")
    chat_bot = factory.create_bot("chat")
    print(chat_bot.perform_task())

    # Testing the creation of DataAnalysisBot
    print("\nTesting DataAnalysisBot Creation:")
    data_bot = factory.create_bot("data")
    print(data_bot.perform_task())

def test_dynamic_bot_registration(factory):
    # Dynamically registering and testing a new bot type
    class ResearchBot:
        def perform_task(self):
            return "ResearchBot performing research."

    factory.register_new_bot_type("research", ResearchBot)
    research_bot = factory.create_bot("research")
    print("\nTesting Dynamically Registered ResearchBot:")
    print(research_bot.perform_task())

def main():
    bot_factory = BotFactory()
    bot_factory.register_new_bot_type("chat", ChatBot)
    bot_factory.register_new_bot_type("data", DataAnalysisBot)
    bot_factory.register_new_bot_type("concurrent", lambda: ConcurrentBot(ChatBot()))

    test_bot_creation(bot_factory)
    test_dynamic_bot_registration(bot_factory)

if __name__ == "__main__":
    main()
