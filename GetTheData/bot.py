from uuid import uuid4
from custom_openai_chat_call import custom_openai_chat_call

class Bot:
  DEFAULT_CONFIG = {
    "name": "Bot",
    "symbol": "B",
    "primer": "You are a helpful assistant.",
    "hub": None,
  }
  def __init__(self, config=DEFAULT_CONFIG, primer=DEFAULT_CONFIG["primer"]):
    self.id = str(uuid4())
    self.name = config["name"]
    self.system_message = primer
    self.last_response = None

  def get_openai_response(self, user_input=None):
    if user_input is None:
      print("Hello, I am " + self.name + ". What would you like to talk about?")
      user_input = input()

    response = custom_openai_chat_call([{"role": "system", "content": self.system_message}, {"role": "user", "content": user_input}])
    response_text = response.choices[0].message.content

    self.last_response = response
    print("Response from OpenAI:\n\n\n")
    print(response_text)
    print("\n\n\n")
    print("Thank you")

if __name__ == "__main__":
  # Create a bot and test it
  bot = Bot()
  bot.get_openai_response()
  bot.get_openai_response("What is your name?")
  bot.get_openai_response("What is your favorite color?")
  bot.get_openai_response("What is your favorite food?")
  bot.get_openai_response("What is your favorite movie?")
  print('\n\n\n')
  print("Last response:")
  print(bot.last_response)
  print('\n\n\n')
  print("End of test")