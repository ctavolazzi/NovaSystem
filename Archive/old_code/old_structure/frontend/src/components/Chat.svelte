<!--
  Chat.svelte - Chat interface component for NovaSystem
  This component provides a conversational interface for interaction with AI agents.
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { Agent, MessageResponse } from '$lib/api';
  import api from '$lib/api';

  // Props
  export let agent: Agent;

  // Local state
  let messages: Array<{
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
  }> = [];
  let inputMessage = '';
  let isLoading = false;
  let error: string | null = null;

  // References
  let chatContainer: HTMLElement;
  let inputField: HTMLTextAreaElement;

  onMount(() => {
    // Focus input field on load
    if (inputField) {
      inputField.focus();
    }

    // Add a system message to start the conversation
    messages = [
      {
        id: 'system-welcome',
        role: 'system',
        content: `Welcome! You're now chatting with ${agent.name}, a ${agent.role}.`,
        timestamp: new Date()
      }
    ];
  });

  // Handle sending a message
  async function sendMessage() {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    inputMessage = '';

    // Add user message to the chat
    const userMessageObj = {
      id: `user-${Date.now()}`,
      role: 'user' as const,
      content: userMessage,
      timestamp: new Date()
    };
    messages = [...messages, userMessageObj];

    // Scroll to bottom
    setTimeout(scrollToBottom, 50);

    // Set loading state
    isLoading = true;
    error = null;

    try {
      // Send message to agent
      const response = await api.sendMessage(agent.id, {
        message: userMessage
      });

      // Add agent response to the chat
      const agentMessageObj = {
        id: `assistant-${Date.now()}`,
        role: 'assistant' as const,
        content: response.content,
        timestamp: new Date()
      };
      messages = [...messages, agentMessageObj];

      // Scroll to bottom
      setTimeout(scrollToBottom, 50);
    } catch (err) {
      console.error('Error sending message:', err);
      error = 'Failed to send message. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  // Handle keypress events
  function handleKeypress(event: KeyboardEvent) {
    // Send message on Enter (without Shift)
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  // Scroll to bottom of chat
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  // Format timestamp
  function formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="flex flex-col h-full">
  <!-- Chat header -->
  <div class="bg-gray-800 text-white p-4 rounded-t-lg flex justify-between items-center">
    <div>
      <h2 class="text-xl font-semibold">{agent.name}</h2>
      <p class="text-sm text-gray-300">{agent.role}</p>
    </div>
    <div class="flex gap-2">
      <button
        class="px-3 py-1 bg-blue-600 rounded text-sm"
        on:click={() => api.reflect(agent.id)}>
        Reflect
      </button>
      <button
        class="px-3 py-1 bg-green-600 rounded text-sm"
        on:click={() => api.summarize(agent.id)}>
        Summarize
      </button>
    </div>
  </div>

  <!-- Chat messages -->
  <div
    bind:this={chatContainer}
    class="flex-1 overflow-y-auto p-4 bg-gray-100 space-y-4">
    {#each messages as message (message.id)}
      <div class={`message ${message.role === 'user' ? 'user-message' : message.role === 'assistant' ? 'assistant-message' : 'system-message'}`}>
        <div class="message-header">
          <span class="message-sender">{message.role === 'user' ? 'You' : message.role === 'assistant' ? agent.name : 'System'}</span>
          <span class="message-time">{formatTime(message.timestamp)}</span>
        </div>
        <div class="message-content">
          {message.content}
        </div>
      </div>
    {/each}

    {#if isLoading}
      <div class="flex justify-center py-2">
        <div class="loading-spinner"></div>
      </div>
    {/if}

    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        {error}
      </div>
    {/if}
  </div>

  <!-- Input area -->
  <div class="p-4 bg-white border-t border-gray-300 rounded-b-lg">
    <div class="flex gap-2">
      <textarea
        bind:this={inputField}
        bind:value={inputMessage}
        on:keypress={handleKeypress}
        class="flex-1 p-2 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows="2"
        placeholder="Type a message..."></textarea>
      <button
        on:click={sendMessage}
        disabled={isLoading || !inputMessage.trim()}
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
        Send
      </button>
    </div>
  </div>
</div>

<style>
  /* Message styling */
  .message {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    max-width: 80%;
  }

  .user-message {
    background-color: #e3f2fd;
    margin-left: auto;
  }

  .assistant-message {
    background-color: white;
    border: 1px solid #e0e0e0;
    margin-right: auto;
  }

  .system-message {
    background-color: #f5f5f5;
    margin: 0 auto;
    max-width: 90%;
    font-style: italic;
    color: #666;
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    font-size: 0.8rem;
  }

  .message-sender {
    font-weight: bold;
  }

  .message-time {
    color: #666;
  }

  .message-content {
    white-space: pre-wrap;
  }

  /* Loading spinner */
  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>