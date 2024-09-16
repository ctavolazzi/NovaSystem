<script lang="ts">
  import LoginGuard from "$lib/components/LoginGuard.svelte";
  import ImgModal from "$lib/pocketbase/ImgModal.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;
</script>

<h1>{data.record.title}</h1>
<LoginGuard><a href="edit"><button>Edit</button></a></LoginGuard>
<article>
  <ImgModal record={data.record} filename={data.record.files[0]} />
  <div class="pre">{data.record.body}</div>
</article>

<style lang="scss">
  h1 {
    border-bottom: dashed 2px;
  }
  article :global(img) {
    float: right;
  }
  .pre {
    white-space: pre-wrap;
  }
</style>
