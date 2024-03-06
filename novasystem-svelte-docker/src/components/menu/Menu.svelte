<script>
    export let menuItems = []; // Expecting an array of { id: string, name: string, link: string }
  </script>
  
  <nav>
    <ul>
      {#each menuItems as { id, name, link }}
        <li key={id}><a href={link}>{name}</a></li>
      {/each}
    </ul>
  </nav>
  
  <style>
    nav {
      /* Basic styling; adjust as needed */
      background-color: #f0f0f0;
      padding: 1rem;
    }
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column; /* Switch to row for a horizontal menu */
    }
    li {
      margin: 0.5rem 0;
    }
    a {
      text-decoration: none;
      color: #333;
      font-weight: bold;
    }
    a:hover {
      text-decoration: underline;
    }
  </style>
  