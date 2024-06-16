import requests
import json
import gradio as gr

# URL for the Ollama REST API
url = "http://localhost:11434/api/generate"

# Request headers
headers = {
    "Content-Type": "application/json"
}

conversation_history = []

def generate_response(user_input):
    if user_input.strip() != "":
        # Append user input to conversation history with sender tag
        conversation_history.append(("User", user_input))

        # Format the full prompt to include conversation history
        full_prompt = "\n".join([f"{sender}: {message}" for sender, message in conversation_history])

        data = {
            "model": "llama2",
            "prompt": full_prompt,
            "stream": False,
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_text = response.text
            data = json.loads(response_text)
            actual_response = data["response"]
            # Append bot response to conversation history
            conversation_history.append(("Bot", actual_response))
        else:
            error_message = f"Request failed with status code: {response.status_code}"
            conversation_history.append(("Bot", error_message))
    
    # Clear the textbox after submission
    return [(message, "User") if sender == "User" else (message, "Bot") for sender, message in conversation_history], ""

def clear_conversation():
    conversation_history.clear()
    return []

# Define the custom CSS
# custom_css = """
#     /* Custom CSS for chat bubbles */
#     .gradio-container { max-width: 700px; margin: auto; }
#     .chat_message { display: flex; }
#     .chat_message.user { justify-content: flex-end; }
#     .chat_message .message { 
#         max-width: 60%; margin: 5px; padding: 10px 15px; border-radius: 18px; line-height: 1.4;
#     }
#     .chat_message.user .message { background-color: #dcf8c6; align-self: end; }
#     .chat_message.bot .message { background-color: #ffffff; align-self: start; }
#     .gr-chatbot-message-list { padding: 0; }
#     .gr-chatbot-message { padding: 0; margin: 2px 0; }
#     .gr-button { margin: 10px 5px; }
# """

custom_css = """
    /* Custom CSS for chat bubbles */
    .gradio-container { max-width: 700px; margin: auto; }
    .gr-chatbot-message { display: flex; width: 100%; }
    .gr-chatbot-message > div:empty { flex-grow: 1; }
    .gr-chatbot-message > div:not(:empty) {
        margin: 5px; padding: 10px 15px; border-radius: 18px;
        line-height: 1.4; max-width: 60%; flex-grow: 0;
    }
    .gr-chatbot-message.user > div:not(:empty) { background-color: #dcf8c6; order: 2; }
    .gr-chatbot-message.bot > div:not(:empty) { background-color: #ffffff; order: 1; }
    .gr-button { margin: 10px 5px; }
"""


with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center;'>Chatbot Interface</h1>")
    chat_history = gr.Chatbot(elem_id="chatbot", show_label=False)
    user_input = gr.Textbox(placeholder="Type your message here...", lines=2, max_lines=2)
    submit_btn = gr.Button("Send")
    clear_btn = gr.Button("Clear")

    user_input.submit(
        generate_response, 
        inputs=user_input, 
        outputs=[chat_history, user_input]
    )
    submit_btn.click(
        generate_response, 
        inputs=user_input, 
        outputs=[chat_history, user_input]
    )
    clear_btn.click(
        clear_conversation, 
        inputs=None, 
        outputs=[chat_history, user_input]
    )

demo.launch()
