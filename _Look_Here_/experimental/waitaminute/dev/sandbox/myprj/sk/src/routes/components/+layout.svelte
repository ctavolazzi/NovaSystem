<script>
  import { base } from "$app/paths";
  import Remote from "./Remote.svelte";

  const components = Object.keys(import.meta.glob("/src/lib/components/**/*.svelte"));
</script>

<Remote />
<div class="wrapper">
  <div class="picker">
    <h1>Components</h1>
    <ul>
      {#each components as c}
        {@const href = c.replace("/src/lib/components/", "")}
        <li>
          <a href={`${base}/components/${href}`}>{href}</a>
        </li>
      {/each}
    </ul>
  </div>
  <div>
    <slot />
  </div>
</div>

<style lang="postcss">
  div.wrapper {
    display: grid;
    grid-template-columns: repeat(4, 5fr);
    grid-auto-rows: minmax(100%, auto);
    gap: 10px;
  }
  .picker {
    width: min-content;
    padding-right: 1rem;
    border-right: solid 1px black;
  }
</style>
