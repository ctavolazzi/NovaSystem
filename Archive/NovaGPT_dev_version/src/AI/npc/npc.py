# src/AI/npc/npc.py

from AI.huggingface_guy import HuggingFaceGuy

class NPC:
    def __init__(self, name):
        self.name = name

def npc_conversation(npc1, npc2, hfg, start_prompt, num_turns=5):
    print(f"Starting a conversation between {npc1.name} and {npc2.name}:")
    print("-" * 50)

    conversation_history = start_prompt

    for _ in range(num_turns):
        # NPC1's turn to speak
        print(f"{npc1.name}: ", end="")
        prompt = f"{conversation_history} {npc1.name}:"
        model_inputs = hfg.tokenize_inputs(prompt)
        response = hfg.generate_text(model_inputs, max_length=50, num_return_sequences=1)[0]
        print(response)
        conversation_history += f" {npc1.name}: {response}"

        # NPC2's turn to speak
        print(f"{npc2.name}: ", end="")
        prompt = f"{conversation_history} {npc2.name}:"
        model_inputs = hfg.tokenize_inputs(prompt)
        response = hfg.generate_text(model_inputs, max_length=50, num_return_sequences=1)[0]
        print(response)
        conversation_history += f" {npc2.name}: {response}"

# Example usage:
if __name__ == "__main__":
    hfg = HuggingFaceGuy("distilgpt2")

    npc1 = NPC("Alice")
    npc2 = NPC("Bob")
    start_prompt = "Alice and Bob meet in the park."

    npc_conversation(npc1, npc2, hfg, start_prompt, num_turns=5)
