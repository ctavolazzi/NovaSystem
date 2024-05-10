import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class Model:
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.params = kwargs

        # Default parameters, can be overridden by kwargs
        self.default_params = {
            'temperature': 0.5,
            'max_tokens': 50,
            'top_p': 1.0,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }

        # Update default parameters with any passed kwargs
        self.default_params.update(self.params)

        # Configuration for different models
        self.config = {
            "davinci": {
                "url": "https://api.openai.com/v1/completions",
                "params": {
                    "model": "text-davinci-003",
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            },
            "gpt-3.5-turbo": {
                "url": "https://api.openai.com/v1/chat/completions",
                "params": {
                    "model": "gpt-3.5-turbo",
                    "messages": [],
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            }
        }

    def make_request(self, prompt, **kwargs):
        if 'davinci' in self.model_name:
            return self._request_openai_completions(prompt, **kwargs)
        elif 'gpt-3.5-turbo' in self.model_name:
            return self._request_openai_chat(prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

    def _request_openai_completions(self, prompt, **kwargs):
        # Update with custom parameters
        request_data = {
            "prompt": prompt,
            **self.config["davinci"]["params"],
            **self.default_params,
            **kwargs
        }

        response = openai.Completion.create(
            model=request_data.pop("model"),
            **request_data
        )
        return response.choices[0].text.strip()

    def _request_openai_chat(self, prompt, **kwargs):
        # Update with custom parameters
        request_data = {
            "messages": [{"role": "system", "content": "You are a helpful assistant."},
                         {"role": "user", "content": prompt}],
            **self.config["gpt-3.5-turbo"]["params"],
            **self.default_params,
            **kwargs
        }

        response = openai.ChatCompletion.create(
            model=request_data.pop("model"),
            **request_data
        )
        return response.choices[0].message.content.strip()


# Usage example
if __name__ == "__main__":
    # Example for text-davinci-003
    davinci_model = Model(
        model_name="text-davinci-003",
        temperature=0.7,
        max_tokens=100
    )
    davinci_prompt = "Explain the significance of the technological singularity."
    davinci_result = davinci_model.make_request(davinci_prompt)
    print("Davinci Response:")
    print(davinci_result)

    # Example for gpt-3.5-turbo
    gpt_model = Model(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=100
    )
    gpt_prompt = "What are the potential benefits of AI in healthcare?"
    gpt_result = gpt_model.make_request(gpt_prompt)
    print("\nGPT-3.5-turbo Response:")
    print(gpt_result)