<script>
  import { remotePath } from "./config";

  let remote = $remotePath;
</script>

<details>
  <summary><b>VSCode Path</b></summary>
  <form on:submit|preventDefault={() => ($remotePath = remote)}>
    <p>
      To allow the "open in VSCode" link to function properly please insert a path like below:<br />
      <b>REMOTE:</b> vscode://vscode-remote/ssh-remote+[HOST]/[PATH_TO_SRC]<br />
      <b>LOCAL:</b> vscode://file/[PATH_TO_SRC] <br />
      <b>EXAMPLE:</b> vscode://file/home/spinspire/dev/project/frontend
    </p>

    <label title="set the remote filepath to open">
      Path:
      <input type="text" bind:value={remote} />
    </label>
    <button>Save</button>
  </form>
</details>

<style>
  button {
    border: 1px solid gray;
    padding: 0.2rem 1rem;
  }
  form {
    padding: 0 1rem;
  }
  label {
    display: inline;
    width: 100% !important;
  }
  input {
    width: 100%;
  }
</style>
