<script lang="ts">
  import "../app.scss";
  import Nav from "$lib/components/Nav.svelte";
  import LoginBadge from "$lib/components/LoginBadge.svelte";
  import { base } from "$app/paths";
  import Alerts from "$lib/components/Alerts.svelte";
</script>

<header>
  <a href={`${base}/`} class="logo">
    <img src={`${base}/favicon.png`} alt="logo" class="logo" />
  </a>
  <Nav />
  <LoginBadge />
</header>

<main>
  <Alerts />
  <slot />
</main>

<footer>
  Copyright &copy; <a href="https://spinspire.com">SpinSpire</a>.
</footer>

<style lang="scss">
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .logo {
      width: 2rem;
      height: 2rem;
    }
    :global(details) {
      margin: 0;
      padding: 0;
    }
  }
  main {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
  }
  footer {
    padding-top: unset; // change water.css
  }
</style>
