<script>
  import { useChat } from 'ai/svelte';

  const { input, handleSubmit, messages } = useChat();
</script>

<style>
  .chat-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .chat-messages {
    margin-bottom: 20px;
  }

  .chat-bubble {
    display: inline-block;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
    max-width: 80%;
  }

  .user-bubble {
    background-color: #007bff;
    color: white;
    align-self: flex-end;
    margin-left: auto;
  }

  .assistant-bubble {
    background-color: #f1f0f0;
    color: black;
  }

  .chat-form {
    display: flex;
  }

  .chat-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-right: 10px;
  }

  .chat-button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
</style>

<div class="chat-container">
  <h1>AI Chat</h1>

  <div class="chat-messages">
    {#each $messages as message}
      <div class="chat-bubble" class:user-bubble={message.role === 'user'} class:assistant-bubble={message.role === 'assistant'}>
        {message.content}
      </div>
    {/each}
  </div>

  <form class="chat-form" on:submit|preventDefault={handleSubmit}>
    <input class="chat-input" type="text" bind:value={$input} placeholder="Type your message..." />
    <button class="chat-button" type="submit">Send</button>
  </form>
</div>


<!-- App.svelte -->
<script>
  import Navbar from './components/Navbar.svelte';
  import Viewport from './components/Viewport.svelte';
  import Terminal from './components/Terminal.svelte';
  import Sidebar from './components/Sidebar.svelte';
</script>

<div class="app-container">
  <Navbar />
  <div class="main-content">
    <Viewport />
    <Terminal />
  </div>
  <Sidebar />
</div>

<style>
  .app-container {
    display: flex;
    height: 100vh;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>