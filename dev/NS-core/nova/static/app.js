class ChatApp {
    constructor() {
        this.sessionId = null;
        this.userId = null;
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.howdyButton = document.getElementById('howdy-button');
        this.chatContainer = document.getElementById('chat-container');
        this.statusElement = document.getElementById('status');
        this.modelSelect = document.getElementById('model-select');

        this.init();
    }

    async init() {
        try {
            // Create a user (in a real app, this would be a login system)
            const userResponse = await fetch('/users/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: 'user_' + Date.now()
                })
            });
            const userData = await userResponse.json();
            this.userId = userData.user_id;

            // Create a chat session
            const sessionResponse = await fetch('/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });
            const sessionData = await sessionResponse.json();
            this.sessionId = sessionData.session_id;

            // Set up event listeners
            this.setupEventListeners();

            // Update status
            this.updateStatus(true, 'Connected');

            // Load chat history
            await this.loadChatHistory();
        } catch (error) {
            console.error('Initialization error:', error);
            this.updateStatus(false, 'Failed to initialize: ' + error.message);
        }
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.howdyButton.addEventListener('click', () => this.sendHowdy());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async loadChatHistory() {
        try {
            const response = await fetch(`/chat/${this.sessionId}/history`);
            const messages = await response.json();
            messages.forEach(msg => this.addMessageToUI(msg.content, msg.role));
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.addMessageToUI('Error: Failed to load chat history', 'system');
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        try {
            this.sendButton.disabled = true;
            this.howdyButton.disabled = true;
            this.modelSelect.disabled = true;
            this.updateStatus(true, 'Thinking...');

            this.addMessageToUI(message, 'user');
            this.messageInput.value = '';

            const response = await fetch(`/chat/${this.sessionId}/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    model: this.modelSelect.value
                })
            });

            const data = await response.json();
            this.addMessageToUI(data.reply, 'assistant');
            this.updateStatus(true, 'Connected');
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToUI(`Error: ${error.message}`, 'system');
            this.updateStatus(false, error.message);
        } finally {
            this.sendButton.disabled = false;
            this.howdyButton.disabled = false;
            this.modelSelect.disabled = false;
            this.messageInput.focus();
        }
    }

    async sendHowdy() {
        this.messageInput.value = 'Howdy';
        await this.sendMessage();
    }

    addMessageToUI(content, role) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        messageElement.textContent = content;
        this.chatContainer.appendChild(messageElement);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    updateStatus(connected, message = '') {
        this.statusElement.textContent = message || (connected ? 'Connected' : 'Disconnected');
        this.statusElement.className = `status ${connected ? 'connected' : ''}`;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

async function executeChain() {
    // Get the system prompt and agents
    const systemPrompt = document.getElementById('systemPrompt').value;
    const agents = getAgents();
    const modelConfig = {
        model: document.getElementById('modelSelect').value
    };

    // Create the request body
    const requestBody = {
        systemPrompt: systemPrompt,
        agents: agents,
        modelConfig: modelConfig
    };

    try {
        const response = await fetch('/execute-chain-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.slice(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        updateChainVisualization(data);
                    } catch (e) {
                        console.error('Error parsing JSON:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        // Update UI to show error
        const visualizationDiv = document.getElementById('chainVisualization');
        visualizationDiv.innerHTML += `<div class="error">Error: ${error.message}</div>`;
    }
}

function updateChainVisualization(agentResult) {
    const visualizationDiv = document.getElementById('chainVisualization');
    const resultDiv = document.createElement('div');
    resultDiv.className = 'agent-result';

    // Sanitize the content to prevent XSS
    const sanitizeHTML = (str) => {
        return str.replace(/[&<>"']/g, function(match) {
            const escape = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            };
            return escape[match];
        });
    };

    resultDiv.innerHTML = `
        <h3>${sanitizeHTML(agentResult.agentName)}</h3>
        <p><strong>Thought:</strong> ${sanitizeHTML(agentResult.thought)}</p>
        <p><strong>Output:</strong> ${sanitizeHTML(agentResult.output)}</p>
    `;
    visualizationDiv.appendChild(resultDiv);

    // Scroll to the bottom to show new content
    visualizationDiv.scrollTop = visualizationDiv.scrollHeight;
}