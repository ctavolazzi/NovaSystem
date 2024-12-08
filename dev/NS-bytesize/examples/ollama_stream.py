from datetime import datetime
import ollama

output_file = "/Users/ctavolazzi/Code/quartz/content/AutoGen-Test-File.md"

def stream_to_console(content: str):
    print(content, end='', flush=True)

def stream_to_file(content: str):
    with open(output_file, 'a') as f:
        f.write(content)
        f.flush()

def handle_stream(stream):
    for chunk in stream:
        content = chunk['message']['content']
        stream_to_console(content)
        stream_to_file(content)

# Initialize markdown file with session header
with open(output_file, 'a') as f:
    f.write(f"\n\n# Ollama Chat Session\n")
    f.write(f"Started at: {datetime.now()}\n\n")

# Initial message
messages = [{
    'role': 'user',
    'content': 'Write one sentence about AI.'
}]

# Stream the response
stream = ollama.chat(
    model='llama3.2',
    messages=messages,
    stream=True,
)

handle_stream(stream)