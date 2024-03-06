<script>
    export let content;
  </script>
  
  <div class="viewport">
    {#if content}
      <p>{content}</p>
    {/if}
  </div>
  
  <style>
    .viewport {
      padding: 16px;
      margin: 10px;
      border: 1px solid #cccccc;
      border-radius: 8px;
      overflow: auto;
    }
  </style>
  