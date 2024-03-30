import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load .env if running as a standalone script
if __name__ == "__main__":
    load_dotenv()

# Set up the OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")
client = OpenAI(api_key=openai_api_key)

def stream_log(prompt, session_folder, settings, model=None):
    # If model is not explicitly provided, check settings or default to "gpt-3.5-turbo"
    model = model or settings.get("model", "gpt-3.5-turbo")

    json_file = os.path.join("chats", session_folder, "chat_data.json")
    log_file_txt = os.path.join("chats", session_folder, "chat_log.txt")
    log_file_md = os.path.join("chats", session_folder, "chat_log.md")

    chat_data = [{"role": "user", "content": prompt}]

    print(f"User: {prompt}")

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": settings["system_message_content"]}] + chat_data,
            stream=True
        )
        print("Assistant: ", end="")
        assistant_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                assistant_response += chunk.choices[0].delta.content
        chat_data.append({"role": "assistant", "content": assistant_response})
        print()  # Add a newline after the assistant's response
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Chat data saved to {os.path.abspath(json_file)}")
        print(f"Chat log saved to {os.path.abspath(log_file_txt)} and {os.path.abspath(log_file_md)}")
        raise

    if chat_data:
        _ensure_directories_and_files_exist(json_file, log_file_txt, log_file_md, settings)
        _save_chat_data(chat_data, json_file, settings)
        _save_chat_log(chat_data, log_file_txt, log_file_md, settings)

def _ensure_directories_and_files_exist(json_file, log_file_txt, log_file_md, settings):
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    os.makedirs(os.path.dirname(log_file_txt), exist_ok=True)
    os.makedirs(os.path.dirname(log_file_md), exist_ok=True)

    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            json.dump({"messages": [{"role": "system", "content": settings["system_message_content"]}]}, file)

    if not os.path.exists(log_file_txt):
        with open(log_file_txt, "w") as file:
            file.write(f"System: {settings['system_message_content']}\n\nChat Log\n")

    if not os.path.exists(log_file_md):
        with open(log_file_md, "w") as file:
            file.write(f"# System: {settings['system_message_content']}\n\n# Chat Log\n")

def _save_chat_data(chat_data, json_file, settings):
    with open(json_file, "r") as file:
        existing_data = json.load(file)
    existing_data["messages"].extend(chat_data)

    with open(json_file, "w") as file:
        json.dump(existing_data, file, indent=2)

def _save_chat_log(chat_data, log_file_txt, log_file_md, settings):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    separator = settings["separator"]

    with open(log_file_txt, "a") as file:
        file.write(f"\n{separator} Chat Log - {timestamp} {separator}\n")
        for message in chat_data:
            file.write(f"{message['role'].title()}: {message['content']}\n")

    with open(log_file_md, "a") as file:
        file.write(f"\n## Chat Log - {timestamp}\n")
        for message in chat_data:
            file.write(f"**{message['role'].title()}:** {message['content']}\n\n")

def _update_metadata(log_file_txt, log_file_md, chat_data, settings):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    separator = settings["separator"]

    with open(log_file_txt, "a") as file:
        file.write(f"\n{separator} Metadata {separator}\n")
        file.write(f"Last Updated: {timestamp}\n")
        file.write(f"Number of Messages: {len(chat_data)}\n")
        file.write(f"Last Message Role: {chat_data[-1]['role'].title()}\n")
        file.write(f"Model Used: {chat_data[0].get('model', 'gpt-3.5-turbo')}\n")
        file.write(f"{separator * 2}\n")

    with open(log_file_md, "a") as file:
        file.write(f"\n## Metadata\n")
        file.write(f"- **Last Updated:** {timestamp}\n")
        file.write(f"- **Number of Messages:** {len(chat_data)}\n")
        file.write(f"- **Last Message Role:** {chat_data[-1]['role'].title()}\n")
        file.write(f"- **Model Used:** {chat_data[0].get('model', 'gpt-3.5-turbo')}\n")

def _display_welcome_message(settings):
    print(settings["separator"] * 30 + " Welcome to the Chatbot! " + settings["separator"] * 30)
    print("To start chatting, simply enter your message and press Enter.")
    print("Type 'quit' to exit the chatbot at any time.")
    print(settings["separator"] * 80)

if __name__ == "__main__":
    settings = {
        "show_welcome_message": True,
        "show_prompt_only_first_message": True,
        "separator": "=",
        "metadata_separator": "-",
        "markdown_bold": "**",
        "max_messages_per_session": 100,
        "model": "gpt-4",
        # "model": "gpt-3.5-turbo",
        "system_message_content": input("Input the role you want this chatbot to take > ")
    }

    if settings["show_welcome_message"]:
        _display_welcome_message(settings)

    session_folder = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_txt = os.path.join("chats", session_folder, "chat_log.txt")
    log_file_md = os.path.join("chats", session_folder, "chat_log.md")

    try:
        chat_data = []
        is_first_message = settings["show_prompt_only_first_message"]
        while len(chat_data) < settings["max_messages_per_session"]:
            if is_first_message:
                prompt = input("\nEnter your message (or 'quit' to exit): ")
                is_first_message = False
            else:
                prompt = input("\n> ")

            if prompt.lower() == "quit":
                _update_metadata(log_file_txt, log_file_md, chat_data, settings)
                print(f"Chat session saved to {os.path.abspath(os.path.join('chats', session_folder))}")
                print("Thank you for using the chatbot. Have a great day!")
                break

            stream_log(prompt, session_folder, settings)
            chat_data.append({"role": "user", "content": prompt})
            chat_data.append({"role": "assistant", "content": ""})

        if len(chat_data) >= settings["max_messages_per_session"]:
            print(f"\nMaximum number of messages per session ({settings['max_messages_per_session']}) reached.")
            _update_metadata(log_file_txt, log_file_md, chat_data, settings)
            print(f"Chat session saved to {os.path.abspath(os.path.join('chats', session_folder))}")
            print("Thank you for using the chatbot. Have a great day!")
    except KeyboardInterrupt:
        _update_metadata(log_file_txt, log_file_md, chat_data, settings)
        print("\nExiting the chatbot...")
        print(f"Chat session saved to {os.path.abspath(os.path.join('chats', session_folder))}")
        print("Thank you for using the chatbot. Have a great day!")
