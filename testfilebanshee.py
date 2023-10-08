import os
from dotenv import load_dotenv
import openai

# Load environment variables from the .env file
load_dotenv()

# Retrieve and debug the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
print("Retrieved API Key:", api_key)

# Validate that the API key exists
if api_key is None:
    raise ValueError("API key not found in environment variables.")

# Define the prompt and model
prompt = "Translate the following English text to French: '{}'"
text = "Hello, world"
model = "gpt-4.0-turbo"  # Replace with actual GPT-4 identifier when available

# Make the API call to OpenAI and store the response
response = openai.Completion.create(
    engine=model,
    prompt=prompt.format(text),
    max_tokens=60,
    api_key=api_key  # Directly providing the API key here
)

# Extract and print the translated text from the API response
translated_text = response.choices[0].text.strip()
print(f"Translated text: {translated_text}")
