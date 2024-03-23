<script lang="ts">
  import DateShow from "$lib/components/DateShow.svelte";
  import LoginGuard from "$lib/components/LoginGuard.svelte";
  import ImgModal from "$lib/pocketbase/ImgModal.svelte";
  import Paginator from "$lib/pocketbase/Paginator.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;
  $: ({ posts } = data);
</script>

<h1>Posts</h1>
<LoginGuard><a href="new/edit"><button>Create New</button></a></LoginGuard>
<Paginator store={posts} />
{#each $posts.items as item}
  {@const dt = new Date(item.updated)}
  <a href={item.id} class="plain">
    <div class="post">
      <DateShow date={item.updated} />
      <blockquote>
        <div class="img">
          <ImgModal record={item} filename={item.files[0]} thumbOnly={true} />
        </div>
        <h2>
          <a href={item.id}>{item.title}</a>
        </h2>
        <div class="pre">{item.body}</div>
      </blockquote>
    </div>
  </a>
{:else}
  <h2>No items to show.</h2>
{/each}
<Paginator store={posts} />

<style lang="scss">
  .post {
    display: flex;
    flex: 1 1 0;
    align-items: center;
    gap: 0.5em;
    h2,
    h4 {
      margin: 0;
    }
    h4 {
      color: var(--text-muted);
    }
    .img {
      float: right;
    }
    blockquote {
      width: 100%;
      max-height: 5.8em;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .pre {
      white-space: pre-wrap;
    }
  }
</style>
