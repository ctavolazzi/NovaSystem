# Default configuration for Ollama
self._ollama_defaults = {
    "config_list": [
        {
            "model": "llama3",
            "base_url": "http://localhost:11434/v1"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}