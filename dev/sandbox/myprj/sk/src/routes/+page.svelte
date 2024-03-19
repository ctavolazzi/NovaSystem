<script lang="ts">
  import { enhance } from "$app/forms";
  import { alerts } from "$lib/components/Alerts.svelte";
  import Dialog from "$lib/components/Dialog.svelte";
  import Spinner, { activityStore } from "$lib/components/Spinner.svelte";
  import { onMount } from "svelte";
  import { readable } from "svelte/store";

  onMount(() => {
    alerts.success("This is success alert!");
    alerts.warning("This is warning alert!");
    alerts.error("This is error alert!");
  });
  let result: any = {};
  let store = activityStore(async function (form: HTMLFormElement) {
    const { action, method } = form;
    const response = await fetch(action, {
      method,
      body: new FormData(form),
    });
    return await response.json();
  });
  async function submit(e: SubmitEvent) {
    result = await store.run(e.target as HTMLFormElement);
  }
</script>

<h1>SpinSpire SvelteKit Starter</h1>
<blockquote>
  Visit <a href="https://github.com/spinspire/tpl">github.com/spinspire/tpl</a> to read the documentation
</blockquote>

<ul>
  <li><a href="/_">pb</a></li>
  <li><a href="/apy/hello">py</a></li>
  <li><a href="/bi">mb</a></li>
</ul>

<details>
  <summary>Collapsible</summary>
  <div>Details ...</div>
</details>

<Dialog>
  <center><h2>Modal Heading</h2></center>
  <ul>
    <li>Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus aliquid</li>
    <li>
      quidem, iure cumque aspernatur molestias, cupiditate iste sunt est omnis quam deserunt autem,
    </li>
    <li>consequuntur maxime vel laudantium exercitationem earum veritatis.</li>
  </ul>
</Dialog>

<form method="post" action="https://httpbin.org/post" on:submit|preventDefault={submit}>
  <input type="text" name="sample-field" value="test this form with a spinner" />
  <button type="submit"><Spinner active={$store} />Button with Spinner</button>
</form>
<pre>{JSON.stringify(result, null, 2)}</pre>

<style lang="scss">
  button {
    display: flex;
    gap: 0.5rem;
  }
</style>
