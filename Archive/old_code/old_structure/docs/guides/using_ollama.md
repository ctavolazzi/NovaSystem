# Using Ollama with NovaSystem

This guide explains how to use Ollama, a local LLM server, with NovaSystem instead of cloud-based AI services.

## What is Ollama?

[Ollama](https://ollama.com/) is an open-source project that lets you run large language models locally on your computer. It provides a simple API for running various open-source models like Llama, Mistral, and others.

## Benefits of Using Ollama with NovaSystem

- **Privacy**: All data stays on your machine
- **No API costs**: Run as many queries as you want without paying per token
- **Offline usage**: No internet connection required after model download
- **Customization**: Fine-tune models for your specific use cases
- **Lower latency**: No network delay for responses

## Setup Instructions

### 1. Install Ollama

Visit [ollama.com/download](https://ollama.com/download) and follow the installation instructions for your operating system:

- **macOS**: Download and install the macOS app
- **Linux**: Run `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows**: Download and install the Windows app

### 2. Download Required Models

After installing Ollama, download the necessary models:

```bash
# Download llama3, a good general-purpose model
ollama pull llama3

# Optional: Download additional models based on your needs
ollama pull mistral
ollama pull gemma:7b
```

### 3. Start Ollama Server

```bash
ollama serve
```

This will start the Ollama server on `http://localhost:11434`.

### 4. Configure NovaSystem to Use Ollama

The setup script should have already configured your `.env` file to use Ollama by default. You can verify this by checking:

```
# NovaSystem/.env
USE_LOCAL_LLM=true
OLLAMA_HOST=http://localhost:11434
DEFAULT_OLLAMA_MODEL=llama3
```

## Available Models

Here are some recommended models to try with NovaSystem:

| Model | Size | Strengths | Pull Command |
|-------|------|-----------|-------------|
| llama3 | 8B | Good all-around model, fast | `ollama pull llama3` |
| mistral | 7B | Strong reasoning capabilities | `ollama pull mistral` |
| gemma:7b | 7B | Google's model, well-rounded | `ollama pull gemma:7b` |
| codellama | 7B | Specialized for code generation | `ollama pull codellama` |
| llama3:70b | 70B | Most capable, needs good GPU | `ollama pull llama3:70b` |

## Switching Models

You can change the default model in the `.env` file:

```
DEFAULT_OLLAMA_MODEL=mistral
```

Or you can specify the model when creating an agent through the API or UI.

## Performance Considerations

- **RAM Requirements**: Models typically require 8-16GB of RAM for smaller models (7B-13B parameters)
- **GPU Acceleration**: Having a GPU significantly improves performance
- **Response Time**: Local models may be slower than cloud-based ones, especially on CPU-only systems
- **Context Window**: The maximum context window varies by model (typically 4K-8K tokens)

## Troubleshooting

### Common Issues and Solutions

1. **"Cannot connect to Ollama server"**
   - Make sure Ollama is running with `ollama serve`
   - Check if the server is accessible at http://localhost:11434/api/tags

2. **Slow responses**
   - Use a smaller model (e.g., `llama3` instead of `llama3:70b`)
   - Ensure you have enough RAM
   - Consider using a GPU if available

3. **Out of memory errors**
   - Reduce model size
   - Close other applications to free up memory
   - Adjust max tokens in requests

4. **Model not found**
   - Run `ollama pull <model_name>` to download the model first

## API Differences

When using Ollama instead of OpenAI, there are some differences in functionality:

- **Message History**: Ollama doesn't maintain conversation state, so NovaSystem handles this internally
- **Structured Output**: Advanced JSON formatting features may be limited
- **Available Models**: Only open-source models are available

## Advanced Configuration

### Custom Ollama Models

You can create custom models with Ollama's Modelfile:

```
# Create a custom model with specific settings
ollama create mycustom -f ./Modelfile
```

Then update your `.env`:
```
DEFAULT_OLLAMA_MODEL=mycustom
```

### Multiple Models

NovaSystem can work with multiple models for different agents. When creating an agent, specify the model:

```json
{
  "agent_type": "dce",
  "name": "CodeHelper",
  "config": {
    "provider_config": {
      "default_model": "codellama"
    }
  }
}
```

## Contributing

If you develop improvements for Ollama integration, please consider contributing them back to the main NovaSystem project!