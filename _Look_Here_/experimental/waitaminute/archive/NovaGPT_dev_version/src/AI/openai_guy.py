# src/AI/openai_guy.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

class OpenAIGuy:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get('OPENAI_API_KEY')

    def get_completion(self, prompt):
        """Returns the completion of the prompt from the OpenAI API."""
        completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are a helpful assistant named Nova. You are part of a team of the NovaSystem, an AI SDK that helps developers build AI-powered applications."},
            {"role": "user", "content": prompt}
          ]
        )

        return completion

if __name__ == "__main__":
    openai_guy = OpenAIGuy()
    prompt = "What is the weather like today?"
    completion = openai_guy.get_completion(prompt)
    print(completion)