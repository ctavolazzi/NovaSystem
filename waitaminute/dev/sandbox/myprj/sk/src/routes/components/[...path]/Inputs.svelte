<script lang="ts">
  import { INPUT_TYPES } from "../config";

  export let value: any = undefined;
  let inputType: keyof typeof INPUT_TYPES = "text";

  // cant bind value without static type, Rich Harris solution: https://stackoverflow.com/a/57393751
  function handleInput(e) {
    value = type.match(/^(number|range)$/) ? +e.target.value : e.target.value;
    // if a custom input has a process function take priority
    if (processor) value = processor(e.target.value);
    console.log(!!processor);
  }
  $: ({ type, attributes = {}, processor } = INPUT_TYPES[inputType]);
</script>

<div class="input">
  <input {type} {...attributes} on:input={handleInput} />
  <select bind:value={inputType}>
    {#each Object.keys(INPUT_TYPES) as name}
      <option value={name}>{name}</option>
    {/each}
  </select>
</div>

<style>
  div.input {
    display: flex;
  }
</style>
