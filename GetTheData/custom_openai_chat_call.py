import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def custom_openai_chat_call(config=[{"role": "system", "content": "You are a helpful assistant."}]):
  messages = []

  if config:
    if type(config) is not str:
      for item in config:
        if item["role"] == "system":
          messages.append(item)
        elif item["role"] == "user":
          messages.append(item)
        elif item["role"] == "assistant":
          messages.append(item)
        else:
          print("Error: Invalid role")
    elif type(config) is str:
      messages.append({"role": "system", "content": config})
      print("Using config: " + config + " as system message\n")
    else:
      print("Error: No config provided")
      print("Using default config")
      messages.append({"role": "system", "content": "You are a helpful assistant."})

  print("Getting response from OpenAI...")
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=messages
  )

  response_text = response.choices[0].message.content
  print("Response from OpenAI:\n\n\n")
  print(response_text)
  print("\n\n\n")
  return response

if __name__ == "__main__":
  print("Would you like to use a custom config? (y/n)")
  if input() == "y":
    print("Please enter your config:")
    user_input = input()
    custom_openai_chat_call(user_input)
  else:
    custom_openai_chat_call()