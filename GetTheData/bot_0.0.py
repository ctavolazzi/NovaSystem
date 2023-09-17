from uuid import uuid4
from collections import deque
from get_custom_openai_chat_completions_response import get_custom_openai_chat_completions_response
import time
import logging

class Bot:
    DEFAULT_CONFIG = {
        "name": "Botticus",
        "system_message": "You are a bot in a system that helps users understand data, answer questions, and make decisions.",
    }

    def __init__(self, name=DEFAULT_CONFIG["name"], system_message=DEFAULT_CONFIG["system_message"], history_size=5):
        self.__id = str(uuid4())
        self.__name = name
        self.__history_size = history_size
        self.__message_history = deque(maxlen=self.__history_size)
        self.__system_message = system_message
        self.__last_response = None
        self.__last_thought = None
        self.__time_of_instantiation = time.time()
        logging.info(f"Bot {self.__name} id {self.__id} created at {self.__time_of_instantiation}")

    def _get_openai_chat_completions_response(self, user_input):
        self.__message_history.append({"role": "user", "content": user_input})
        messages_to_sent_to_openai = [{"role": "system", "content": self.__system_message}]
        messages_to_sent_to_openai.extend(list(self.__message_history))

        try:
            response = get_custom_openai_chat_completions_response(messages_to_sent_to_openai)
        except Exception as e:
            logging.error(f"An error occurred when making a request to the OpenAI API: {e}")
            return None

        self.__message_history.append({"role": "assistant", "content": response.choices[0].message.content})
        return response

    def think_about(self, str_input):
        response = self._get_openai_chat_completions_response(str_input)
        if response is not None:
            logging.info(f"Bot {self.__name} is thinking about {str_input} and wants to say {response.choices[0].message.content}")
            self.__last_thought = response

    def respond_to(self, str_input):
        response = self._get_openai_chat_completions_response(str_input)
        if response is not None:
            logging.info(f"Bot {self.__name} is responding to {str_input} with {response.choices[0].message.content}")
            self.__last_response = response

    def identify(self):
        logging.info(f"I am {self.__name} and my id is {self.__id}")

    # Getters and setters
    def get_last_response(self):
        return self.__last_response

    def get_last_thought(self):
        return self.__last_thought

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_time_of_instantiation(self):
        return self.__time_of_instantiation

    def get_system_message(self):
        return self.__system_message

    def get_message_history(self):
        return list(self.__message_history)

    def get_history_size(self):
        return self.__history_size

    def set_name(self, name):
        assert isinstance(name, str), "Name must be a string."
        self.__name = name
        logging.info(f"Bot {self.__id} name changed to {self.__name}")

    def set_system_message(self, system_message):
        assert isinstance(system_message, str), "System message must be a string."
        self.__system_message = system_message
        logging.info(f"Bot {self.__id} system message changed to {self.__system_message}")

    def set_history_size(self, history_size):
        assert isinstance(history_size, int), "History size must be an integer."
        self.__history_size = history_size
        self.__message_history = deque(maxlen=self.__history_size)  # Reinitialize message history with new size
        logging.info(f"Bot {self.__id} history size changed to {self.__history_size}")

    def set_message_history(self, message_history):
        assert isinstance(message_history, list), "Message history must be a list."
        self.__message_history = deque(message_history, maxlen=self.__history_size)
        logging.info(f"Bot {self.__id} message history changed")

    def set_last_response(self, last_response):
        assert isinstance(last_response, str), "Last response must be a string."
        self.__last_response = last_response
        logging.info(f"Bot {self.__id} last response changed")

    # Overloaded methods
    def __str__(self):
        return f"Bot {self.__name} id {self.__id} created at {self.__time_of_instantiation}"

    def __repr__(self):
        return f"Bot {self.__name} id {self.__id} created at {self.__time_of_instantiation}"

    def __eq__(self, other):
        return self.__id == other.__id

    def print_state(self):
        print(f"""
    ╔═══════════════════════════════════════════════╗
    ║              BOT STATE - {self.__name}              ║
    ╠═══════════════════════════════════════════════╣
    ║ ID: {self.__id}
    ║ Time of instantiation: {self.__time_of_instantiation}
    ║ System message: {self.__system_message}
    ║ History size: {self.__history_size}
    ║ Message history: {self.__message_history}
    ║ Last response: {'None' if self.__last_response is None else self.__last_response.choices[0].message.content}
    ║ Last thought: {'None' if self.__last_thought is None else self.__last_thought.choices[0].message.content}
    ╚═══════════════════════════════════════════════╝
        """)

        print(f"""
    _  _ ____ ____ ____ ____ _  _ ____
    |__| |    |  | |    |  | |  | | __
    |  | |___ |__| |___ |__| |__| |__]

    ===[ BOT STATUS ]===
    Identification Number: {self.__id}
    Time of Activation: {self.__time_of_instantiation}
    System Message: {self.__system_message}
    Message History Capacity: {self.__history_size}
    Message History: {self.__message_history}
    Last Response: {'None' if self.__last_response is None else self.__last_response.choices[0].message.content}
    Last Thought: {'None' if self.__last_thought is None else self.__last_thought.choices[0].message.content}

    <====]====-  END OF REPORT  -====[====
    """)

        print(f"""
    ____________________________________________________________________________________________________
    |                                                                                                  |
    |   ██████╗  █████╗ ████████╗████████╗██╗     ███████╗███████╗████████╗                            |
    |   ██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██║     ██╔════╝██╔════╝╚══██╔══╝                            |
    |   ██████╔╝███████║   ██║      ██║   ██║     █████╗  ███████╗   ██║                               |
    |   ██╔══██╗██╔══██║   ██║      ██║   ██║     ██╔══╝  ╚════██║   ██║                               |
    |   ██████╔╝██║  ██║   ██║      ██║   ███████╗███████╗███████║   ██║                               |
    |   ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚═╝                               |
    |                                                                                                  |
    |                                          BOT STATUS                                               |
    |                                                                                                  |
    | Identification Number: {self.__id}                                                                       |
    | Time of Activation: {self.__time_of_instantiation}                                                      |
    | System Message: {self.__system_message}                                                                  |
    | Message History Capacity: {self.__history_size}                                                          |
    | Message History: {self.__message_history}                                                                |
    | Last Response: {'None' if self.__last_response is None else self.__last_response.choices[0].message.content} |
    | Last Thought: {'None' if self.__last_thought is None else self.__last_thought.choices[0].message.content}   |
    |__________________________________________________________________________________________________|
    """)


if __name__ == "__main__":
    bot = Bot()
    bot.identify()
    # bot.think_about("What is the meaning of life?")
    # print(bot.get_last_thought().choices[0].message.content)
    # bot.respond_to("The meaning of life is to be happy.")
    # print(bot.get_last_response().choices[0].message.content)
    # print(bot.get_message_history())
    # bot.think_about("What is the meaning of life?")
    # print(bot.get_last_thought())
    bot.print_state()