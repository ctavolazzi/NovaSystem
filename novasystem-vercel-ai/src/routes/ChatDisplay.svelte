<!-- ChatDisplay.svelte
<script>
  import { onMount } from 'svelte';
  
  let chats = [];
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      const response = await fetch('/api/chat');
      if (response.ok) {
        chats = await response.json();
      } else {
        error = 'Failed to fetch chats';
      }
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });
</script>

<main>
  <h2>Chat History</h2>
  {#if loading}
    <p>Loading chats...</p>
  {:else if error}
    <p>Error: {error}</p>
  {:else}
    {#if chats.length === 0}
      <p>No chats found.</p>
    {:else}
      <ul>
        {#each chats as chat}
          <li>
            <h3>{chat.title}</h3>
            <ul>
              {#each chat.messages as message}
                <li>{message.role}: {message.content}</li>
              {/each}
            </ul>
          </li>
        {/each}
      </ul>
    {/if}
  {/if}
</main> -->