# Set model name from arguments or use defaults
self.model_name = model_name or ("llama3" if use_ollama else "gpt-4o-mini")