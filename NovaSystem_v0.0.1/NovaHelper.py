import time
<<<<<<< HEAD
import logging
import openai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve and debug the OpenAI API key from environment variables
os.getenv("OPENAI_API_KEY")

# Validate that the API key exists
if os.getenv("OPENAI_API_KEY") is None:
    raise ValueError("API key not found in environment variables.")

# # Define the prompt and model
# prompt = "Translate the following English text to French: '{}'"
# text = "Hello, world"
# model = "gpt-3.5-turbo"  # Replace with actual GPT-4 identifier when available

=======
>>>>>>> b6f8c82 (🪄 📌 🔎x)

class NovaHelper():
  _default_delay = 0.022

  def __init__(self):
    self.classification = 'NovaHelper'

  def test(self):
    self.stc(f'Testing NovaHelper...\n')
    self.stc(f'classification: {self.classification}\n')
    self.stc(f'{self.classification} class instantiated successfully.')

  def stream_to_console(self, message, delay=_default_delay):
    for char in message:
      print(char, end='', flush=True)
      time.sleep(delay)

  def stc(self, message, delay=_default_delay):
    self.stream_to_console(message, delay)

<<<<<<< HEAD
  def fetch_response_from_default_API(self, request={'API': 'openai', 'request': {'prompt': 'Hello, world', 'model': 'gpt-3.5-turbo', 'max_tokens': 60}}):
    # Unpack request
    print(f'Helper Calling API...\n')
    for k, v in request.items():
      print(f'{k}: {v}')
    # Make API call and return response
    pass

  def make_api_call(self, callback=None):
    # Make API call and return response
    print(type(callback))
    if type(callback) is str:
      # Make API to OpenAI and return resopnse
      # response = openai.Completion.create(
      #   model = 'gpt-3.5-turbo',
      #   prompt='This is a test',
      #   max_tokens=5,
      #   api_key=os.getenv("OPENAI_API_KEY")
      # )

      openai.api_key = os.getenv("OPENAI_API_KEY")
      response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=callback,
        max_tokens=50,
        temperature=.5
      )

      return response

    if callback is not None:
      callback()
    else:
      self.fetch_response_from_default_API()
    pass

=======
>>>>>>> b6f8c82 (🪄 📌 🔎x)
def stc(message, delay=0.022):
  helper = NovaHelper()
  helper.stream_to_console(message, delay)

if __name__ == "__main__":
  helper = NovaHelper()
  helper.test()
