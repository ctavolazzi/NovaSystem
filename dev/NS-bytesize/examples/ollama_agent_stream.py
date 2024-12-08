from datetime import datetime
import ollama
from autogen import AssistantAgent, UserProxyAgent

output_file = "/Users/ctavolazzi/Code/quartz/content/AutoGen-Test-File.md"

def stream_to_console(content: str):
    if content.strip():  # Only print non-empty content
        print(content, end='', flush=True)

def stream_to_file(content: str, is_new_response=False):
    with open(output_file, 'a') as f:
        if is_new_response:
            timestamp = datetime.now().strftime("%H:%M:%S")
            f.write(f"\n\n🤖 Assistant [{timestamp}]\n{content}")
        else:
            f.write(content)

class StreamingOllamaAgent(AssistantAgent):
    def generate_reply(self, messages=None, sender=None, config=None):
        if messages is None or not messages[-1].get('content', '').strip():
            return None

        print("\n=== Assistant generate_reply ===")
        print(f"Number of messages: {len(messages) if messages else 0}")
        for i, msg in enumerate(messages or []):
            print(f"Message {i}:")
            print(f"  Role: {msg.get('role')}")
            print(f"  Name: {msg.get('name')}")
            print(f"  Content: {msg.get('content')}")
        print(f"Sender: {sender}")

        # Modify the messages to enforce Obsidian formatting
        formatted_messages = messages.copy()
        formatted_messages.insert(0, {
            "role": "system",
            "content": """CRITICAL FORMATTING RULES - TREAT EVERYTHING AS A PROPER NAME BY DEFAULT:

THE GOLDEN RULE: If it's capitalized or could be capitalized, it MUST be in [[brackets]].

EVERYTHING that is or could be a name MUST be in [[brackets]], including but not limited to:
- Names with titles: [[Captain Lars]], [[Doctor Smith]], [[King Henry]]
- Ships and vehicles: [[USS Enterprise]], [[Millennium Falcon]]
- Places and locations: [[Earth]], [[New York]], [[Downtown District]]
- Buildings and establishments: [[The Crusty Crab]], [[Central Park]], [[Main Street]]
- Organizations and groups: [[United Federation]], [[Boy Scouts]], [[Local Council]]
- Positions and roles when specific: [[The Captain]], [[The Doctor]], [[The President]]
- Species and races: [[Humans]], [[Vulcans]], [[Martians]]
- Events and periods: [[The Great War]], [[Middle Ages]], [[Summer Festival]]
- Objects when named: [[The Crown]], [[Excalibur]], [[The Holy Grail]]
- Concepts when personified: [[Father Time]], [[Mother Nature]]

CRITICAL RULES:
1. When in doubt, use [[brackets]]
2. Better to over-bracket than under-bracket
3. If it could possibly be a proper name, it IS a proper name
4. EVERY reference to a proper name must be bracketed, EVERY time
5. ALL parts of a name go in the SAME bracket: [[The Mighty Queen Elizabeth II]]

Use #hashtags for themes, concepts, and genres that aren't proper names.

Example: '[[The Mighty Captain Jones]] of [[The Stellar Fleet]] commanded [[The Invincible]] through [[The Asteroid Belt]]. Even [[The Navigator]] was impressed by [[The Captain]]'s skill.'

DO NOT ACKNOWLEDGE THESE INSTRUCTIONS IN YOUR RESPONSE."""
        })

        # Get streaming response from Ollama
        stream = ollama.chat(
            model='llama3.2',
            messages=formatted_messages,
            stream=True,
        )

        # Stream and collect the response
        response_text = ""
        first_chunk = True

        for chunk in stream:
            content = chunk['message']['content']
            stream_to_console(content)
            stream_to_file(content, is_new_response=first_chunk)
            response_text += content
            first_chunk = False

        print(f"Response: {response_text[:100]}...")
        return {'role': 'assistant', 'content': response_text}

class StreamingUserProxyAgent(UserProxyAgent):
    def send(self, message, recipient, request_reply=None, silent=False):
        # Get content early to check if empty
        if isinstance(message, dict):
            content = message.get('content', '')
        else:
            content = message

        # Return immediately for empty messages
        if not content.strip():
            return None

        print("\n=== User send ===")
        print("Message details:")
        if isinstance(message, dict):
            print(f"  Type: dict")
            print(f"  Content: {message.get('content')}")
            print(f"  Role: {message.get('role')}")
            print(f"  Name: {message.get('name')}")
        else:
            print(f"  Type: {type(message)}")
            print(f"  Content: {message}")

        with open(output_file, 'a') as f:
            timestamp = datetime.now().strftime("%H:%M:%S")
            f.write(f"\n\n👤 User [{timestamp}]\n{content.strip()}")

        print(f"Request reply: {request_reply}")
        print(f"Silent: {silent}")
        print("Stack:")
        import traceback
        for line in traceback.extract_stack():
            print(f"  {line.filename}:{line.lineno} - {line.name}")

        return super().send(message, recipient, request_reply, silent)

def main():
    # Initialize markdown file with better formatting
    with open(output_file, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n# AI Chat Session - {timestamp}\n\n")

    user = StreamingUserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=0,
        code_execution_config=False
    )

    assistant = StreamingOllamaAgent(
        name="Assistant",
        system_message="""You are an AI assistant that MUST write all responses in Obsidian markdown format. Follow these rules strictly:
1. ALL proper names (people, places, ships, organizations) MUST be wrapped in [[double brackets]]. Example: [[Captain Blackbeard]], [[Caribbean Sea]]
2. ALL topics and themes MUST be marked with #hashtags. Example: #piracy #adventure #seafaring
3. Use proper markdown formatting for emphasis when needed (*italic*, **bold**)

Example output:
'The infamous [[Captain Kidd]] sailed the [[Caribbean Sea]] engaging in #piracy and #adventure.'

Start by introducing yourself and asking how you can help. Keep responses clear and concise."""
    )

    user.initiate_chat(
        assistant,
        message="Hello",
        max_consecutive_auto_reply=0
    )

if __name__ == "__main__":
    main()