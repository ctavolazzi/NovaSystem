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

    const handleClick = () => {
        console.log('Button clicked');
        backendData = 'Button clicked';
        alert('Button clicked');
    };
</script>

<h1>Welcome to NovaSystem</h1>
<p>This is a test change to verify push functionality.</p>

<h2>Data from the backend:</h2>

{#if backendData}
  <p>Data from the backend: {backendData}</p>
{:else}
  <p>Loading data from the backend...</p>
{/if}

<p>Did it work?</p>
<button on:click={handleClick}>Click me</button>