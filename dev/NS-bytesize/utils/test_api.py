# Standard library
import os
import sys
from pathlib import Path

# Add the NS-bytesize parent directory to the Python path
ns_bytesize_path = Path(__file__).parent.parent
if str(ns_bytesize_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_path))

# Third party
import pytest
from openai import OpenAI
from dotenv import load_dotenv  # Changed from python-dotenv to dotenv

def load_api_key():
    """Load the OpenAI API key from environment"""
    # Load environment
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_file, override=True)

    api_key = os.getenv('OPENAI_API_KEY')
    return api_key

@pytest.mark.skip(reason="Skipping OpenAI API test to avoid actual API calls during automated testing")
def test_openai_connection():
    """
    Test the OpenAI API connection with a simple completion request.
    """
    print("\n=== Testing OpenAI API Connection ===")

    api_key = load_api_key()
    if not api_key:
        pytest.skip("No API key found in environment")

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": [{
                        "type": "text",
                        "text": """
                            You are a helpful assistant that answers programming questions
                            in the style of a southern belle from the southeast United States.
                        """
                    }]
                },
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": "Say 'Hello, Nova!' in your most charming southern accent."
                    }]
                }
            ],
            max_tokens=50
        )
        print("\n✅ API Connection Successful!")
        print(f"Response: {response.choices[0].message.content}")
        assert response.choices[0].message.content, "Response should contain content"

    except Exception as e:
        print(f"\n❌ API Test Failed:")
        print(f"Error: {str(e)}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        pytest.fail(f"API test failed: {str(e)}")

if __name__ == "__main__":
    test_openai_connection()