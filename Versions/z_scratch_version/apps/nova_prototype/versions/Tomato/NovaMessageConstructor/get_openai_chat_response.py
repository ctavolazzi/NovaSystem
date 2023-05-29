import openai
import os
from dotenv import load_dotenv

messages = [
        {"role": "system", "content": "You are a helpful assistant."},

        {"role": "user", "content": "Who won the world series in 2020?"},

        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},

        {"role": "user", "content": "Where was it played?"}
    ]

def get_openai_chat_response(message_array):
    load_dotenv()

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=message_array
    )

    response_content = response.choices[0].message['content']

    print(response_content)

def test():
    get_openai_chat_response(messages)

if __name__ == "__main__":
    test()