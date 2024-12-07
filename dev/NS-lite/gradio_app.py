import gradio as gr
import requests
import sys
from io import StringIO
import time
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "nemotron-mini"

class OllamaBot:
    def __init__(self, name, role_description):
        self.name = name
        self.role_description = role_description

    def think(self, prompt: str) -> str:
        data = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": self.role_description
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        print(f"\n[{self.name}] Sending request to Ollama...")
        try:
            response = requests.post(OLLAMA_API_URL, json=data)
            response.raise_for_status()
            print(f"[{self.name}] Got response from Ollama")

            # Get the last line of the response for streaming output
            lines = response.text.strip().split('\n')
            last_response = lines[-1]

            result = json.loads(last_response)
            if "message" in result and "content" in result["message"]:
                content = result["message"]["content"]
                if content.strip():  # Check if content is not empty
                    return content.strip()
                else:
                    return f"[ERROR: Empty response from model]"
            else:
                return f"[ERROR: Unexpected response format: {result}]"
        except Exception as e:
            print(f"[{self.name}] Error: {str(e)}")
            return f"[ERROR calling Ollama: {e}]"

class MinimalOllamaNovaProcess:
    def __init__(self):
        self.dce = OllamaBot("DCE", """You are the Discussion Continuity Expert.
            Keep the conversation coherent and summarize insights effectively.
            Focus on clear, actionable summaries.""")

        self.cae = OllamaBot("CAE", """You are the Critical Analysis Expert.
            Critique proposals and highlight potential issues.
            Be specific about concerns and suggest improvements.""")

        self.domain_expert = OllamaBot("DomainExpert", """You are a Domain Expert.
            Break down problems into clear components.
            Suggest practical, implementable improvements.""")

    def run(self, user_problem: str):
        # Problem Unpacking
        insights = self.domain_expert.think(f"Analyze this problem in detail:\n{user_problem}")
        summary = self.dce.think(f"Summarize these insights clearly:\n{insights}")
        critique = self.cae.think(f"Critically evaluate this summary:\n{summary}")

        print("\n=== Problem Analysis ===")
        print(f"Expert Insights: {insights}")
        print(f"Summary: {summary}")
        print(f"Critical Review: {critique}")

        # Solution Development
        improved_strat = self.domain_expert.think(
            f"""Based on the problem and critique, propose a detailed solution strategy.
            Original Problem: {user_problem}
            Initial Analysis: {insights}
            Critique: {critique}"""
        )

        improved_summary = self.dce.think(f"Provide a clear, actionable summary of this strategy:\n{improved_strat}")
        final_critique = self.cae.think(f"Evaluate this solution strategy:\n{improved_summary}")

        print("\n=== Solution Development ===")
        print(f"Proposed Strategy: {improved_strat}")
        print(f"Strategy Summary: {improved_summary}")
        print(f"Final Evaluation: {final_critique}")

def capture_output(func):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        func()
        output = mystdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output

def run_nova_process(problem: str, temperature: float = 0.7) -> str:
    if not problem.strip():
        return "Please enter a problem first!"

    def process():
        nova = MinimalOllamaNovaProcess()
        enhanced_problem = f"""
Task: Analyze and solve the following problem using the Nova Process.
Problem Statement: {problem}
Requirements:
- Break down the problem into clear components
- Provide specific, actionable insights
- Suggest concrete improvements
- Evaluate potential issues
Please provide a detailed analysis.
"""
        nova.run(enhanced_problem)

    try:
        return capture_output(process)
    except Exception as e:
        return f"Error: {str(e)}\nPlease try again with a more specific problem statement."

# Create the Gradio interface
demo = gr.Interface(
    fn=run_nova_process,
    inputs=[
        gr.Textbox(
            lines=4,
            placeholder="Describe your problem or challenge in detail...",
            label="Problem Description"
        ),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.7,
            label="Temperature (Creativity)",
            info="Higher values = more creative, lower = more focused"
        )
    ],
    outputs=[
        gr.Textbox(
            lines=15,
            label="Process Output",
            show_copy_button=True
        )
    ],
    title="Nova Process Interface",
    description="""
    Enter a detailed problem description and let the Nova Process analyze it.
    Tips:
    - Be specific about your problem
    - Include relevant context
    - Mention any constraints or requirements
    """,
    theme="soft",
    flagging_mode="never",
    examples=[
        ["We need to improve our team's code review process. Currently, reviews take too long and often miss important issues.", 0.7],
        ["Our startup needs to decide between building our own authentication system or using a third-party solution.", 0.6]
    ]
)

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0")