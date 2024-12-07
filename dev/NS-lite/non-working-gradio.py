"""
Nova Reasoning UI - A Gradio interface for interacting with Ollama language models.
This module provides a web interface for asking questions and receiving structured responses
with reasoning steps and final answers.
"""

import asyncio
import logging
from typing import Tuple, Optional, Dict, Any
from ollama import AsyncClient
import gradio as gr
import sys
import os
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from pathlib import Path
import json
import platform
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import numpy as np
from collections import defaultdict
import networkx as nx
from wordcloud import WordCloud
from transformers import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nova_system.log')
    ]
)
logger = logging.getLogger(__name__)

try:
    asr = pipeline("automatic-speech-recognition", "facebook/wav2vec2-base-960h")
    classifier = pipeline("text-classification")
    logger.info("Successfully loaded ML models")
except Exception as e:
    logger.error(f"Error loading ML models: {e}")
    asr = None
    classifier = None

def create_session_log() -> Path:
    """Create a new session log directory and files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    session_dir = log_dir / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create markdown report file
    report_file = session_dir / "reasoning_report.md"
    with open(report_file, "w") as f:
        f.write(f"# Nova Reasoning Session Report\n\n")
        f.write(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    return session_dir

def log_reasoning_step(session_dir: Path, step_num: int, content: str, step_type: str = "reasoning"):
    """Log a reasoning step to both markdown and JSON formats."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Update markdown report
    report_file = session_dir / "reasoning_report.md"
    with open(report_file, "a") as f:
        if step_type == "question":
            f.write(f"\n## User Question\n")
            f.write(f"*{timestamp}*\n\n")
            f.write(f"{content}\n")
        elif step_type == "reasoning":
            f.write(f"\n### Step {step_num}: Reasoning\n")
            f.write(f"*{timestamp}*\n\n")
            f.write(f"{content}\n")
        elif step_type == "answer":
            f.write(f"\n## Final Answer\n")
            f.write(f"*{timestamp}*\n\n")
            f.write(f"{content}\n")
            f.write("\n---\n")  # Add separator after each Q&A session

    # Also save as structured JSON for potential analysis
    json_file = session_dir / "reasoning_steps.json"
    step_data = {
        "timestamp": timestamp,
        "step_number": step_num,
        "type": step_type,
        "content": content
    }

    try:
        if json_file.exists():
            with open(json_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(step_data)

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        logger.error(f"Error saving JSON log: {e}")

def get_system_info() -> Dict[str, Any]:
    """Gather system information for logging."""
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f}GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f}GB"
        }
    except Exception as e:
        logger.error(f"Error gathering system info: {e}")
        return {}

def log_session_metadata(session_dir: Path, model: str):
    """Log session metadata including system information."""
    metadata_file = session_dir / "session_metadata.json"
    try:
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "system_info": get_system_info()
        }

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    except Exception as e:
        logger.error(f"Error saving session metadata: {e}")

def create_visualizations(session_dir: Path, steps_data: list):
    """Create visualizations for the reasoning process."""
    viz_dir = session_dir / "visualizations"
    viz_dir.mkdir(exist_ok=True)

    try:
        # 1. Timeline visualization
        plt.figure(figsize=(12, 6))
        timestamps = [datetime.strptime(step['timestamp'], "%H:%M:%S") for step in steps_data]
        base_time = timestamps[0]
        relative_times = [(t - base_time).total_seconds() for t in timestamps]

        plt.plot(relative_times, range(len(steps_data)), 'bo-')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Step Number')
        plt.title('Reasoning Process Timeline')
        plt.grid(True)
        plt.savefig(viz_dir / 'timeline.png')
        plt.close()

        # 2. Step Duration Analysis
        plt.figure(figsize=(10, 6))
        step_durations = []
        for i in range(len(timestamps)-1):
            duration = (timestamps[i+1] - timestamps[i]).total_seconds()
            step_durations.append(duration)

        sns.barplot(x=range(len(step_durations)), y=step_durations)
        plt.xlabel('Step Transition')
        plt.ylabel('Duration (seconds)')
        plt.title('Step Duration Analysis')
        plt.savefig(viz_dir / 'step_durations.png')
        plt.close()

        # 3. Content Length Analysis
        plt.figure(figsize=(10, 6))
        content_lengths = [len(step['content'].split()) for step in steps_data]

        sns.barplot(x=[step['type'] for step in steps_data],
                   y=content_lengths)
        plt.xticks(rotation=45)
        plt.xlabel('Step Type')
        plt.ylabel('Content Length (words)')
        plt.title('Content Length by Step Type')
        plt.tight_layout()
        plt.savefig(viz_dir / 'content_analysis.png')
        plt.close()

        return viz_dir

    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        return None

def create_reasoning_flow_diagram(session_dir: Path, steps_data: list):
    """Create a network diagram showing the flow of reasoning."""
    G = nx.DiGraph()

    # Create nodes for each step
    for step in steps_data:
        node_id = f"{step['type']}_{step['step_number']}"
        G.add_node(node_id,
                  type=step['type'],
                  content=step['content'][:50] + "...",
                  timestamp=step['timestamp'])

    # Create edges between consecutive steps
    for i in range(len(steps_data)-1):
        from_node = f"{steps_data[i]['type']}_{steps_data[i]['step_number']}"
        to_node = f"{steps_data[i+1]['type']}_{steps_data[i+1]['step_number']}"
        G.add_edge(from_node, to_node)

    # Create the visualization
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=2000, font_size=8, arrows=True)
    plt.savefig(session_dir / "visualizations" / "reasoning_flow.png")
    plt.close()

def create_word_cloud(session_dir: Path, steps_data: list):
    """Create word clouds for reasoning steps and final answer."""
    reasoning_text = " ".join([s['content'] for s in steps_data if s['type'] == 'reasoning'])
    answer_text = " ".join([s['content'] for s in steps_data if s['type'] == 'answer'])

    # Reasoning word cloud
    wc_reasoning = WordCloud(width=800, height=400, background_color='white')
    wc_reasoning.generate(reasoning_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc_reasoning)
    plt.axis('off')
    plt.title('Reasoning Steps Word Cloud')
    plt.savefig(session_dir / "visualizations" / "reasoning_wordcloud.png")
    plt.close()

    # Answer word cloud
    if answer_text:
        wc_answer = WordCloud(width=800, height=400, background_color='white')
        wc_answer.generate(answer_text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wc_answer)
        plt.axis('off')
        plt.title('Final Answer Word Cloud')
        plt.savefig(session_dir / "visualizations" / "answer_wordcloud.png")
        plt.close()

def analyze_reasoning_patterns(steps_data: list) -> dict:
    """Analyze patterns in the reasoning process."""
    analysis = {
        "step_transitions": defaultdict(int),
        "common_phrases": defaultdict(int),
        "step_complexity": [],
        "temporal_patterns": []
    }

    # Analyze transitions between steps
    for i in range(len(steps_data)-1):
        transition = f"{steps_data[i]['type']} -> {steps_data[i+1]['type']}"
        analysis["step_transitions"][transition] += 1

    # Analyze complexity of each step
    for step in steps_data:
        words = step['content'].split()
        complexity = {
            "word_count": len(words),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "type": step['type']
        }
        analysis["step_complexity"].append(complexity)

    return analysis

def create_session_report(session_dir: Path):
    """Create a summary of the reasoning session."""
    try:
        summary_file = session_dir / "session_summary.md"
        with open(summary_file, "w") as f:
            f.write("# Session Summary\n\n")
            f.write(f"Session completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    except Exception as e:
        logger.error(f"Error creating session report: {str(e)}")

def find_free_port(start_port: int = 7860, max_tries: int = 100) -> int:
    """Find an available port starting from the given port number."""
    port = start_port
    while port < start_port + max_tries:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                logger.info(f"Found available port: {port}")
                return port
        except OSError:
            port += 1
    raise OSError(f"No free ports found in range {start_port}-{start_port + max_tries}")

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events to enable hot reloading."""
    def __init__(self, port: int):
        self.port = port
        super().__init__()

    def on_modified(self, event):
        if event.src_path.endswith('main.py'):
            logger.info("Source file modified. Initiating server restart...")
            time.sleep(1)
            try:
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                logger.error(f"Error during restart: {str(e)}", exc_info=True)

class NovaOutput:
    """Container for Nova's output that can be passed between systems"""
    def __init__(self, reasoning: str = "", answer: str = "", context: str = ""):
        self.reasoning = reasoning
        self.answer = answer
        self.context = context  # Previous system's context
        self.full_context = []  # Track all systems' outputs

    def add_to_context(self, system_name: str, output: Tuple[str, str]):
        """Add a system's output to the context history"""
        reasoning, answer = output
        self.full_context.append({
            "system": system_name,
            "reasoning": reasoning,
            "answer": answer
        })
        # Update context with previous answer
        self.context = f"Previous system ({system_name}) concluded: {answer}"

    def __str__(self):
        return f"NovaOutput(reasoning={self.reasoning[:50]}..., answer={self.answer[:50]}...)"

async def nova_system(user_input: str, system_name: str, context: str = "",
                     model: str = "nemotron-mini") -> Tuple[str, str]:
    """Single Nova system that can be chained"""
    logger.info(f"Starting {system_name} with context: {context}")

    # Customize system message based on context
    system_msg = (
        f"You are {system_name}, an advanced problem-solving AI. "
        f"{context}\n"
        "First think step-by-step and write your reasoning "
        "under '### Reasoning Steps:'. "
        "Then write your final answer under '### Final Answer:'. "
        "Do not include extra text outside these headings."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_input}
    ]

    try:
        client = AsyncClient()
        stream = await client.chat(model=model, messages=messages, stream=True)

        reasoning_steps = ""
        final_answer = ""
        current_section = None

        async for part in stream:
            if 'message' in part and 'content' in part['message']:
                token = part['message']['content']

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

        return reasoning_steps.strip(), final_answer.strip()

    except Exception as e:
        logger.error(f"Error in {system_name}: {str(e)}")
        return f"Error: {str(e)}", "An error occurred"

async def nova_pipeline(user_input: str) -> NovaOutput:
    """Chain multiple Nova systems together"""
    output = NovaOutput()

    # First system: Initial Analysis
    reasoning, answer = await nova_system(
        user_input=user_input,
        system_name="Nova Analyzer",
        context="Analyze the question and break it down into key components."
    )
    output.add_to_context("Nova Analyzer", (reasoning, answer))

    # Second system: Deep Reasoning
    reasoning, answer = await nova_system(
        user_input=user_input,
        system_name="Nova Reasoner",
        context=output.context,
        model="nemotron-mini"  # Using a different model for variety
    )
    output.add_to_context("Nova Reasoner", (reasoning, answer))

    # Third system: Final Synthesis
    reasoning, answer = await nova_system(
        user_input=user_input,
        system_name="Nova Synthesizer",
        context=output.context
    )
    output.add_to_context("Nova Synthesizer", (reasoning, answer))

    # Set final output
    output.reasoning = reasoning
    output.answer = answer

    return output

def run_pipeline(user_input: str):
    """Run the pipeline and update Gradio outputs in real-time"""
    try:
        # Initialize empty outputs
        yield ["Initializing...", "", "", ""]

        async def run_async_pipeline():
            output = NovaOutput()

            # First system: Initial Analysis
            yield ["Running Nova Analyzer...", "", "", ""]
            reasoning, answer = await nova_system(
                user_input=user_input,
                system_name="Nova Analyzer",
                context="Analyze the question and break it down into key components."
            )
            output.add_to_context("Nova Analyzer", (reasoning, answer))
            yield [format_context(output.full_context), reasoning, answer, ""]

            # Second system: Deep Reasoning
            yield [format_context(output.full_context), reasoning, answer, "Running Nova Reasoner..."]
            reasoning, answer = await nova_system(
                user_input=user_input,
                system_name="Nova Reasoner",
                context=output.context,
                model="nemotron-mini"
            )
            output.add_to_context("Nova Reasoner", (reasoning, answer))
            yield [format_context(output.full_context), reasoning, answer, ""]

            # Third system: Final Synthesis
            yield [format_context(output.full_context), reasoning, answer, "Running Final Synthesis..."]
            reasoning, answer = await nova_system(
                user_input=user_input,
                system_name="Nova Synthesizer",
                context=output.context
            )
            output.add_to_context("Nova Synthesizer", (reasoning, answer))

            # Final output
            context_md = format_context(output.full_context)
            yield [context_md, reasoning, answer, "Complete!"]

        async def process_pipeline():
            async for update in run_async_pipeline():
                yield update

        # Run the pipeline using asyncio.run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            generator = process_pipeline()
            while True:
                try:
                    result = loop.run_until_complete(generator.__anext__())
                    yield result
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        yield [f"Error: {str(e)}", "", "", "Error occurred"]

def format_context(context_list):
    """Format the context history as markdown"""
    context_md = "## Analysis Chain\n\n"
    for step in context_list:
        context_md += f"### {step['system']}\n"
        context_md += f"**Reasoning:**\n{step['reasoning']}\n\n"
        context_md += f"**Answer:**\n{step['answer']}\n\n"
        context_md += "---\n\n"
    return context_md

# Create Gradio interface
with gr.Blocks(title="Nova Multi-System Reasoning") as demo:
    gr.Markdown("## Nova Multi-System Analysis")

    with gr.Row():
        user_input = gr.Textbox(
            lines=2,
            label="Enter your question",
            placeholder="Ask anything..."
        )

    with gr.Row():
        submit = gr.Button("Analyze", variant="primary")
        clear = gr.Button("Clear")

    with gr.Column():
        status = gr.Markdown("Status: Ready")
        chain_output = gr.Markdown(label="Analysis Chain")
        current_reasoning = gr.Textbox(
            lines=10,
            label="Current System Reasoning",
            show_copy_button=True
        )
        current_answer = gr.Textbox(
            lines=5,
            label="Current System Answer",
            show_copy_button=True
        )

    submit.click(
        fn=run_pipeline,
        inputs=user_input,
        outputs=[chain_output, current_reasoning, current_answer, status],
        api_name="predict"
    )

    clear.click(
        lambda: ("", "", "", "Status: Ready"),
        outputs=[chain_output, current_reasoning, current_answer, status]
    )

if __name__ == "__main__":
    try:
        port = find_free_port()

        # Initialize file watcher for hot reloading
        observer = None
        if "--no-reload" not in sys.argv:
            event_handler = FileChangeHandler(port)
            observer = Observer()
            observer.schedule(event_handler, path=".", recursive=False)
            observer.start()
            logger.info("Hot reloading enabled")

        # Launch the Gradio interface
        logger.info("Starting Nova Reasoning UI...")
        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=port,
            show_error=True,
            quiet=False,
            debug=True
        )

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        if observer:
            observer.stop()
            observer.join()

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if observer:
            observer.stop()
            observer.join()
        sys.exit(1)

    finally:
        if observer:
            observer.stop()
            observer.join()
