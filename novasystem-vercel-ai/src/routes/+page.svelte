<script>
  import { useChat } from 'ai/svelte';
 
  const { input, handleSubmit, messages } = useChat();
</script>
 
<main>
  <ul>
    {#each $messages as message}
      <li>{message.role}: {message.content}</li>
    {/each}
  </ul>
  <form on:submit={handleSubmit}>
    <input bind:value={$input} />
    <button type="submit">Send</button>
  </form>
</main>

<style> main { display: flex; flex-direction: column; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9; } ul { list-style-type: none; } li { margin-bottom: 5px; padding: 5px; background-color: #fff; border-radius: 5px; } input { padding: 5px; margin-right: 5px; border: 1px solid #ccc; border-radius: 3px; } button { padding: 5px 10px; background-color: #007bff; color: #fff; border: none; border-radius: 3px; cursor: pointer; } </style>