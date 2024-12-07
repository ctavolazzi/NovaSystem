from flask import Flask, request, render_template_string, Response
import asyncio
import logging
import json
import sys
import os
import time
import socket
from datetime import datetime
from pathlib import Path
import platform
import psutil
import networkx as nx
from collections import defaultdict
from ollama import AsyncClient
import queue
import threading
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('nova_system.log')]
)
logger = logging.getLogger(__name__)

class NovaOutput:
    def __init__(self, reasoning: str = "", answer: str = "", context: str = ""):
        self.reasoning = reasoning
        self.answer = answer
        self.context = context
        self.full_context = []

    def add_to_context(self, system_name: str, output):
        reasoning, answer = output
        self.full_context.append({
            "system": system_name,
            "reasoning": reasoning,
            "answer": answer
        })
        self.context = f"Previous system ({system_name}) concluded: {answer}"

    def __str__(self):
        return f"NovaOutput(reasoning={self.reasoning[:50]}..., answer={self.answer[:50]}...)"

async def nova_system(user_input: str, system_name: str, context: str = "", model: str = "nemotron-mini"):
    logger.info(f"Starting {system_name} with context: {context}")
    system_msg = f"""You are {system_name}, an advanced problem-solving AI. {context}

You must format your response exactly like this example:

### Reasoning Steps:
1. First step of reasoning
2. Second step of reasoning
3. Third step of reasoning

### Final Answer:
The final conclusion based on the reasoning steps.

Remember: Always use these exact headings and format."""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_input}
    ]

    try:
        client = AsyncClient()
        logger.info(f"{system_name}: Sending request to Ollama...")
        stream = await client.chat(model=model, messages=messages, stream=True)

        full_response = ""
        reasoning_steps = ""
        final_answer = ""
        current_section = None

        async for part in stream:
            if 'message' in part and 'content' in part['message']:
                token = part['message']['content']
                full_response += token

                # Yield each token as it arrives
                yield {
                    "type": "token",
                    "system": system_name,
                    "content": token,
                    "section": current_section
                }

                if "### Reasoning Steps:" in token:
                    current_section = "reasoning"
                    token = token.replace("### Reasoning Steps:", "")
                elif "### Final Answer:" in token:
                    current_section = "answer"
                    token = token.replace("### Final Answer:", "")

                if current_section == "reasoning":
                    reasoning_steps += token
                elif current_section == "answer":
                    final_answer += token

        # Return final structured output
        yield {
            "type": "complete",
            "system": system_name,
            "reasoning": reasoning_steps.strip(),
            "answer": final_answer.strip()
        }

    except Exception as e:
        logger.error(f"Error in {system_name}: {str(e)}", exc_info=True)
        yield {
            "type": "error",
            "system": system_name,
            "content": str(e)
        }

def format_token_update(data):
    """Format a token update for display"""
    if data['type'] == 'token':
        return f"""
        <div class="token-update" style="color: {
            'blue' if data['section'] == 'reasoning'
            else 'green' if data['section'] == 'answer'
            else 'gray'
        };">
            {data['content']}
        </div>
        """
    return ""

app = Flask(__name__)

def create_response_stream():
    """Create a queue for streaming responses"""
    return queue.Queue()

def stream_template(template_name, **context):
    """Stream template by yielding new data"""
    app.update_template_context(context)
    template = app.jinja_env.get_template(template_name)
    rv = template.stream(context)
    return rv

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Nova Reasoning UI</title>
    <style>
        .error { color: red; }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
        }
        .system-output {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        #live-stream {
            font-family: monospace;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-height: 100px;
            max-height: 400px;
            overflow-y: auto;
        }
        .token-update {
            display: inline;
            animation: fadeIn 0.2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body style="font-family: sans-serif; margin: 40px; max-width: 1200px; margin: 0 auto; padding: 20px;">
    <h1>Nova Multi-System Analysis</h1>
    <form id="analysisForm">
        <label>Enter your question:</label><br>
        <textarea name="user_input" style="width: 100%; min-height: 100px;"
                  placeholder="Enter your question here..." required></textarea><br><br>
        <button type="submit" id="submitBtn">Analyze</button>
    </form>
    <div id="status" class="status">Ready</div>
    <hr>
    <div id="live-stream"></div>
    <hr>
    <div id="results"></div>

    <script>
        const form = document.getElementById('analysisForm');
        const status = document.getElementById('status');
        const results = document.getElementById('results');
        const liveStream = document.getElementById('live-stream');
        const submitBtn = document.getElementById('submitBtn');
        let eventSource;

        function appendToken(token) {
            liveStream.insertAdjacentHTML('beforeend', token);
            liveStream.scrollTop = liveStream.scrollHeight;
        }

        form.onsubmit = async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const question = formData.get('user_input');

            if (!question.trim()) {
                status.textContent = 'Please enter a question';
                return;
            }

            // Reset UI
            submitBtn.disabled = true;
            results.innerHTML = '';
            liveStream.innerHTML = '';
            status.textContent = 'Starting analysis...';

            if (eventSource) {
                eventSource.close();
            }

            eventSource = new EventSource(`/stream?question=${encodeURIComponent(question)}`);

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'token') {
                        appendToken(data.content);
                    } else if (data.type === 'status') {
                        status.textContent = data.content;
                    } else if (data.type === 'update') {
                        results.innerHTML = data.content;
                    } else if (data.type === 'complete') {
                        status.textContent = 'Analysis complete';
                        eventSource.close();
                        submitBtn.disabled = false;
                    }
                } catch (error) {
                    console.error('Error parsing event data:', error);
                }
            };

            eventSource.onerror = (error) => {
                console.error('EventSource failed:', error);
                status.textContent = 'Error: Connection failed';
                eventSource.close();
                submitBtn.disabled = false;
            };
        };
    </script>
</body>
</html>
"""

def send_update(queue, update_type, content):
    """Send an update to the client"""
    queue.put(json.dumps({
        'type': update_type,
        'content': content
    }))

@app.route('/stream')
def stream():
    """Stream updates to the client"""
    question = request.args.get('question', '')
    if not question:
        return Response('data: {"type": "error", "content": "No question provided"}\n\n',
                       mimetype='text/event-stream')

    def generate(question_text):
        q = create_response_stream()

        def process_nova():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def run_pipeline():
                    # First system: Initial Analysis
                    send_update(q, 'status', 'Running Initial Analysis...')
                    async for update in nova_system(
                        user_input=question_text,
                        system_name="Nova Analyzer",
                        context="Analyze the question and break it down into key components."
                    ):
                        if update['type'] == 'token':
                            send_update(q, 'token', format_token_update(update))
                        elif update['type'] == 'complete':
                            reasoning = update['reasoning']
                            answer = update['answer']
                            output = NovaOutput()
                            output.add_to_context("Nova Analyzer", (reasoning, answer))

                    # Second system: Deep Reasoning
                    send_update(q, 'status', 'Running Deep Reasoning...')
                    async for update in nova_system(
                        user_input=question_text,
                        system_name="Nova Reasoner",
                        context=output.context
                    ):
                        if update['type'] == 'token':
                            send_update(q, 'token', format_token_update(update))
                        elif update['type'] == 'complete':
                            reasoning = update['reasoning']
                            answer = update['answer']
                            output.add_to_context("Nova Reasoner", (reasoning, answer))

                    # Third system: Final Synthesis
                    send_update(q, 'status', 'Running Final Synthesis...')
                    async for update in nova_system(
                        user_input=question_text,
                        system_name="Nova Synthesizer",
                        context=output.context
                    ):
                        if update['type'] == 'token':
                            send_update(q, 'token', format_token_update(update))
                        elif update['type'] == 'complete':
                            reasoning = update['reasoning']
                            answer = update['answer']
                            output.add_to_context("Nova Synthesizer", (reasoning, answer))

                    # Send complete signal
                    send_update(q, 'complete', 'Analysis complete')

                loop.run_until_complete(run_pipeline())
                loop.close()

            except Exception as e:
                logger.error(f"Error in pipeline: {str(e)}", exc_info=True)
                send_update(q, 'status', f'Error: {str(e)}')
            finally:
                q.put(None)  # Signal the end of updates

        # Start processing in a separate thread
        thread = threading.Thread(target=process_nova)
        thread.start()

        # Stream updates to the client
        while True:
            result = q.get()
            if result is None:
                break
            yield f"data: {result}\n\n"

    return Response(generate(question), mimetype='text/event-stream')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Redirect POST requests to use the streaming endpoint
        return render_template_string(html_template)
    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
