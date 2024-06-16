<!-- src/routes/+page.svelte -->
<script>
	import { writable } from 'svelte/store';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import MessageList from '$lib/components/MessageList.svelte';
	
	const messages = writable([]);
	let inputMessage = '';
	
	async function sendMessage() {
	  const content = inputMessage.trim();
	  if (content) {
		messages.update(current => [...current, { role: 'user', content }]);
		inputMessage = '';
	
		const response = await fetch('/api/chat', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({ messages: [{ role: 'user', content }] })
		});
	
		if (response.ok) {
		  const { response: aiResponse } = await response.json();
		  messages.update(current => [...current, { role: 'ai', content: aiResponse }]);
		} else {
		  console.error('Failed to send message');
		}
	  }
	}
  </script>
  
  <svelte:head>
	<title>Chat with AI</title>
  </svelte:head>
  
  <section>
	<MessageList {messages} />
	<ChatInput bind:value={inputMessage} on:sendMessage={sendMessage} />
  </section>
  

  

  

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}

	h1 {
		width: 100%;
	}

	.welcome {
		display: block;
		position: relative;
		width: 100%;
		height: 0;
		padding: 0 0 calc(100% * 495 / 2048) 0;
	}

	.welcome img {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		display: block;
	}
</style>
