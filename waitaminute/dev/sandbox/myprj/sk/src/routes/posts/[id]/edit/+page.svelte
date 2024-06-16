<script lang="ts">
  import { goto } from "$app/navigation";
  import FileInput from "$lib/components/FileInput.svelte";
  import { save } from "$lib/pocketbase";
  import type { PageData } from "./$types";

  export let data: PageData;
  let files: FileList;
  async function submit() {
    await save("posts", { ...data.record, files });
    await goto("..");
  }
</script>

<form on:submit|preventDefault={submit}>
  <label>
    <span>title</span>
    <input bind:value={data.record.title} type="text" />
  </label>
  <FileInput bind:files />
  <label>
    <span>body</span>
    <textarea bind:value={data.record.body} rows="10" />
  </label>
  <button>Save</button>
</form>
