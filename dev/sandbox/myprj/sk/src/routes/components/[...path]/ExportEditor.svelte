<script lang="ts">
  import type { ComponentType } from "svelte";
  import Inputs from "./Inputs.svelte";
  import { remotePath } from "../config";

  export let component: ComponentType;
  export let bindings: { [label: string]: any } = {};
</script>

<div class="form">
  <h3>Exports:</h3>
  <a href={`${$remotePath}/src/routes/components/config.ts:1`}>Add custom export types</a>
  {#if component}
    {#each Object.keys(component.$$.props) as item}
      <!-- svelte-ignore a11y-label-has-associated-control -->
      <label>
        {item}
        <Inputs bind:value={bindings[item]} />
      </label>
    {/each}
  {/if}
</div>

<slot {bindings} />

<style>
  div.form {
    padding: 1rem;
  }
</style>
