import asyncio
from ollama import AsyncClient
import gradio as gr
import sys
import os
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

async def simple_nova_interaction(user_input, model="nemotron-mini"):
    print(f"Starting interaction with model: {model}")
    system_msg = (
        "You are Nova, an advanced problem-solving AI. "
        "When given a user query, first think step-by-step and write down your reasoning "
        "under the heading '### Reasoning Steps:'. "
        "Then, write the final answer under the heading '### Final Answer:'. "
        "Do not include extra text outside these headings."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_input}
    ]

    try:
        print("Connecting to Ollama...")
        client = AsyncClient()
        print("Sending request to model...")
        stream = await client.chat(model=model, messages=messages, stream=True)

        full_response = ""
        reasoning_steps = ""
        final_answer = ""
        current_section = None

        print("Processing response stream...")
        async for part in stream:
            if 'message' in part and 'content' in part['message']:
                token = part['message']['content']
                full_response += token

                # Split the full response when we have complete sections
                if "### Reasoning Steps:" in full_response and "### Final Answer:" in full_response:
                    parts = full_response.split("### Reasoning Steps:")
                    if len(parts) > 1:
                        reasoning_parts = parts[1].split("### Final Answer:")
                        reasoning_steps = reasoning_parts[0].strip()
                        if len(reasoning_parts) > 1:
                            final_answer = reasoning_parts[1].strip()
                elif "### Reasoning Steps:" in full_response:
                    parts = full_response.split("### Reasoning Steps:")
                    if len(parts) > 1:
                        reasoning_steps = parts[1].strip()

                print(f"Token: {token}")  # Debug output

        print("Stream processing complete")
        return reasoning_steps.strip(), final_answer.strip()

    except Exception as e:
        print(f"Error in simple_nova_interaction: {str(e)}")
        raise e

def run_interaction(user_input):
    print(f"Received question: {user_input}")  # Debug output
    try:
        reasoning, answer = asyncio.run(simple_nova_interaction(user_input))
        print(f"Got response - Reasoning: {reasoning[:100]}...")  # Debug output
        print(f"Got response - Answer: {answer[:100]}...")  # Debug output
        return reasoning, answer
    except Exception as e:
        print(f"Error in run_interaction: {str(e)}")  # Debug output
        return f"Error: {str(e)}", "An error occurred"

with gr.Blocks(title="Nova Reasoning UI") as demo:
    gr.Markdown("## Ask Nova Anything")
    user_input = gr.Textbox(lines=2, label="Enter your question")
    submit = gr.Button("Get Reasoning & Answer")

    reasoning_output = gr.Textbox(lines=10, label="Nova's Reasoning Steps")
    answer_output = gr.Textbox(lines=5, label="Nova's Final Answer")

    submit.click(
        fn=run_interaction,
        inputs=user_input,
        outputs=[reasoning_output, answer_output]
    )

if __name__ == "__main__":
    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, port):
            self.port = port
            super().__init__()

        def on_modified(self, event):
            if event.src_path.endswith('mrn-test.py'):
                print("\nFile changed. Restarting server...")
                # Wait a bit to ensure the port is released
                time.sleep(1)
                os.execv(sys.executable, ['python'] + sys.argv)

    def find_free_port(start_port=7860):
        """Find a free port starting from the given port number."""
        port = start_port
        while port < start_port + 100:  # Try 100 ports
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                port += 1
        raise OSError("No free ports found")

    try:
        port = find_free_port()

        observer = None
        if "--no-reload" not in sys.argv:
            event_handler = FileChangeHandler(port)
            observer = Observer()
            observer.schedule(event_handler, path=".", recursive=False)
            observer.start()

        demo.launch(
            server_name="0.0.0.0",    # Allow external connections
            server_port=port,         # Use the found free port
            show_error=True,          # Show detailed error messages
            quiet=False,              # Show all logs
            debug=True               # Enable debug mode
        )
    except KeyboardInterrupt:
        if observer:
            observer.stop()
            observer.join()
    except Exception as e:
        print(f"Error: {e}")
        if observer:
            observer.stop()
            observer.join()
        sys.exit(1)
    finally:
        if observer:
            observer.stop()
            observer.join()
