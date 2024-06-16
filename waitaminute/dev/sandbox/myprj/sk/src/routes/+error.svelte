<script lang="ts">
  import { page } from "$app/stores";
</script>

<div class="carbon-fiber">
  <h1>{$page.status}<br />{$page.error?.message}</h1>
</div>

<style>
  div {
    display: flex;
    flex: 1 1 auto;
    margin: 10rem;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-size: 300%;
  }
</style>
