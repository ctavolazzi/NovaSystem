# src/AI/huggingface_guy.py

from transformers import AutoModelForCausalLM, AutoTokenizer

class HuggingFaceGuy:
    def __init__(self, model_name):
        # Load the model
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to("cpu")

        # Load the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Set the padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def tokenize_inputs(self, texts, device='cpu'):
        # Tokenize the texts and prepare model inputs
        model_inputs = self.tokenizer(texts, return_tensors="pt", padding=True).to(device)
        return model_inputs

    def generate_text(self, model_inputs, max_length=100, num_return_sequences=1):
        # Generate text with controlled length and parameters
        generated_ids = self.model.generate(
            input_ids=model_inputs['input_ids'],
            attention_mask=model_inputs['attention_mask'],
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            num_beams=3,
            no_repeat_ngram_size=2,
            early_stopping=True,
            temperature=1.0,  # Adjusting the randomness
            do_sample=True,
        )
        generated_texts = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return generated_texts[0].strip()


if __name__ == "__main__":
    hfg = HuggingFaceGuy("distilgpt2")
    prompt = "What is the vibe like in California?"
    model_inputs = hfg.tokenize_inputs(prompt)
    generated_texts = hfg.generate_text(model_inputs)
    print(generated_texts)
