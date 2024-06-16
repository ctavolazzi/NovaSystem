# # Load model directly
# from transformers import AutoTokenizer, AutoModelForCausalLM

# tokenizer = AutoTokenizer.from_pretrained("01-ai/Yi-34B")
# model = AutoModelForCausalLM.from_pretrained("01-ai/Yi-34B")

# # Use a pipeline as a high-level helper
# from transformers import pipeline

# pipe = pipeline("text-generation", model="01-ai/Yi-34B")