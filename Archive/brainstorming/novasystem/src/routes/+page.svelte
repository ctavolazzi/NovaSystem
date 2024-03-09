<script>
    import { onMount } from 'svelte';
  
    let name = ''; // Declare the name variable here
    let messages = []; // Array to store chat messages
  
    async function handleSubmit() {
      // Push user's message to the messages array
      messages = [...messages, { sender: 'user', text: name }];
      // Clear the input field after submitting
      name = '';
  
      // Call the OpenAI API to get the response
      const response = await fetch('/your-openai-endpoint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: name }) // Send user's message to the API
      });
  
      const data = await response.json();
      // Push the AI's response to the messages array
      messages = [...messages, { sender: 'AI', text: data.reply }];
    }
  
    // Scroll to the bottom of the chat window when messages update
    onMount(() => {
      const chatWindow = document.getElementById('chat-window');
      chatWindow.scrollTop = chatWindow.scrollHeight;
    });
  </script>
  
  <h1>Welcome to SvelteKit</h1>
  <p>Hello Big Mama</p>
  <div id="chat-window">
    {#each messages as message}
      {#if message.sender === 'user'}
        <p>You: {message.text}</p>
      {:else if message.sender === 'AI'}
        <p>AI: {message.text}</p>
      {/if}
    {/each}
  </div>
  <form on:submit|preventDefault={handleSubmit}>
      <input type="text" bind:value={name} />
      <button type="submit">Send</button>
  </form>
  <p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>
  