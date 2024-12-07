import datetime
import asyncio
from ollama import AsyncClient, ChatResponse

async def nova_brain_interaction(user_input, model="llama3.2"):
    # Instructions to the model:
    # We ask it to produce reasoning steps under "### Reasoning Steps:"
    # and the final answer under "### Final Answer:" headings.
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

    # We'll use the streaming interface so we can parse as tokens come in.
    client = AsyncClient()
    stream = await client.chat(model=model, messages=messages, stream=True)

    reasoning_steps = ""
    final_answer = ""
    current_section = None

    # We'll accumulate tokens as they stream in, line by line
    async for part in stream:
        if 'message' in part and 'content' in part['message']:
            token = part['message']['content']

            # If we see the heading for reasoning steps, switch section
            if "### Reasoning Steps:" in token:
                # There might be text before or after, so let's split carefully.
                segments = token.split("### Reasoning Steps:")
                # If there's content before ### Reasoning Steps:, discard or add to final_answer?
                # Since instructions say no extraneous text, we assume none before.
                # Now we are in reasoning section
                current_section = "reasoning"
                # Everything after ### Reasoning Steps: goes to reasoning
                if len(segments) > 1:
                    reasoning_steps += segments[1]
                else:
                    # The token might just contain "### Reasoning Steps:" at the end
                    # and the next token will have the reasoning
                    pass
                continue

            # If we see the heading for final answer, switch section
            if "### Final Answer:" in token:
                segments = token.split("### Final Answer:")
                # Append what was before final answer heading to reasoning if current_section is reasoning
                if current_section == "reasoning":
                    reasoning_steps += segments[0]
                # Now switch to final answer section
                current_section = "final"
                # If there's something after ### Final Answer:, append to final_answer
                if len(segments) > 1:
                    final_answer += segments[1]
                continue

            # If we are currently in reasoning section, append to reasoning
            if current_section == "reasoning":
                reasoning_steps += token
            # If we are currently in final answer section, append to final_answer
            elif current_section == "final":
                final_answer += token
            # If we haven't hit any heading yet, it's stray text (shouldn't happen due to instructions)
            # We can ignore or store. We'll ignore here.

    return reasoning_steps.strip(), final_answer.strip()

def save_reasoning_to_md(reasoning_text):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chain_of_thought_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Chain of Thought\n\n")
        f.write(reasoning_text)
    print(f"Reasoning steps saved to {filename}")

if __name__ == "__main__":
    user_question = "Explain the concept of overfitting in machine learning."
    # Choose your model: "llama3.2" or "nemotron-mini"
    chosen_model = "llama3.2"

    reasoning, answer = asyncio.run(nova_brain_interaction(user_question, model=chosen_model))

    if reasoning:
        save_reasoning_to_md(reasoning)
    if answer:
        print("Nova's final answer:")
        print(answer)
