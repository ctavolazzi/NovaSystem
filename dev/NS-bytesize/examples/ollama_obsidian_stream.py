from datetime import datetime
import ollama

output_file = "/Users/ctavolazzi/Code/quartz/content/AutoGen-Test-File.md"

def stream_to_console(content: str):
    print(content, end='', flush=True)

def stream_to_file(content: str, is_new_response=False):
    with open(output_file, 'a') as f:
        if is_new_response:
            f.write("\n\n### Assistant\n")
        f.write(content)
        f.flush()

def handle_stream(stream):
    first_chunk = True
    for chunk in stream:
        content = chunk['message']['content']
        stream_to_console(content)
        stream_to_file(content, is_new_response=first_chunk)
        first_chunk = False

# Initialize markdown file with session header
with open(output_file, 'a') as f:
    f.write(f"\n\n# Ollama Chat Session\n")
    f.write(f"Started at: {datetime.now()}\n\n")
    f.write("### User\n")
    f.write("Write one sentence about AI.\n")

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