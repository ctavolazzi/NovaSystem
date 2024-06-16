<svelte:options accessors />

<script lang="ts">
  import type { ComponentType } from "svelte";
  import type { PageData } from "./$types";
  import { cleanComponentPath, remotePath } from "../config";
  import ExportEditor from "./ExportEditor.svelte";

  export let data: PageData;
  let component: ComponentType;

  let unique = {};

  // Allows manual reload of component
  function restart() {
    unique = {}; // every {} is unique, {} === {} evaluates to false
  }
</script>

<a
  href={`${$remotePath}/src/lib/components/${cleanComponentPath(data.path)}:1`}
  title="If this is failing, you should edit the path settings above.">Open component in VSCode</a
>

{#await import(`../../../lib/components/${data.path}`)}
  <span>Loading...</span>
{:then value}
  <ExportEditor {component} let:bindings>
    <button on:click={restart}>Reload Component</button>
    {#key unique}
      <div style="resize:both; overflow: auto; border: solid 2px;">
        <svelte:component this={value.default} bind:this={component} {...bindings} />
      </div>
    {/key}
  </ExportEditor>
{/await}
