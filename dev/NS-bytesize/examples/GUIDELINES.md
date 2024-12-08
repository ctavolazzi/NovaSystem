# Guidelines for AutoGen Implementation

## Core Principles
1. **Single Responsibility**
   - Each function should do ONE thing
   - Each agent should have ONE clear role
   - Keep configurations separate from logic

2. **Error Handling**
   - Always check for null/empty responses
   - Log both the error and its cause
   - Provide clear error messages to users
   - Handle timeouts gracefully

3. **Configuration Guidelines**
   - DO NOT use OpenAI-specific parameters with Ollama
   - Required Ollama config parameters:
     ```python
     {
         "model": "llama3.2",  # NEVER use llama2
         "base_url": "http://localhost:11434/v1",
         "api_key": "ollama"
     }
     ```
   - Optional but useful parameters:
     ```python
     {
         "temperature": 0.7,
         "timeout": 120,  # in seconds
         "context_length": 4096
     }
     ```

4. **Agent Communication**
   - Clear conversation history between chats
   - Set max_turns to prevent infinite loops
   - Use explicit termination conditions
   - Validate messages before processing

5. **Testing Steps**
   1. First test Ollama connection
   2. Then test single agent response
   3. Then test agent-to-agent communication
   4. Finally test full conversation flow

6. **Common Issues & Solutions**
   - Infinite loops: Use `max_turns` and `max_consecutive_auto_reply`
   - No response: Check Ollama server status
   - Timeout: Adjust timeout values
   - Wrong model: Verify model is pulled with `ollama list`

7. **Debugging Process**
   1. Check Ollama server is running
   2. Verify model is available
   3. Test API connection
   4. Check message format
   5. Validate agent configurations
   6. Review conversation flow

8. **Code Organization**
   ```python
   # 1. Imports
   # 2. Configuration functions
   # 3. Logging functions
   # 4. Agent creation functions
   # 5. Conversation handling functions
   # 6. Main execution
   ```

9. **Message Flow**
   ```
   User Input -> User Proxy -> Analyzer -> User Proxy -> Responder -> User Proxy -> Output
   ```

10. **Best Practices**
    - Log every step of the conversation
    - Clear error messages
    - Graceful degradation
    - Clean exit handling
    - Resource cleanup

## Testing Checklist
- [ ] Ollama server running
- [ ] Model available
- [ ] Configuration valid
- [ ] Single message flow works
- [ ] Multi-turn conversation works
- [ ] Error handling works
- [ ] Cleanup works

## Common Commands
```bash
# Check Ollama status
ollama list

# Pull model if needed
ollama pull llama3.2

# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/v1/chat/completions -d '{"model":"llama3.2","messages":[{"role":"user","content":"test"}]}'
```

## References
- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [AutoGen Docs](https://microsoft.github.io/autogen/)