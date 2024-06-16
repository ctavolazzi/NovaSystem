<!-- <h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p> -->

<script>
    import { onMount } from 'svelte';
    
    let backendData = '';
    
    onMount(async () => {
      try {
        const response = await fetch('https://novasystem-backend-5bc4a8329298.herokuapp.com/');
        backendData = await response.text();
      } catch (error) {
        console.error('Error fetching data from the backend:', error);
      }
    });
    </script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

{#if backendData}
  <p>Data from the backend: {backendData}</p>
{:else}
  <p>Loading data from the backend...</p>
{/if}