# receipes

Ready to go templates/starter-kits for commonly used tech-stacks. Just `npx degit spinspire/recipes/something myprj`

_Note 1: I'm trying to keep this README short. For a more detailed explanation, see [this article](https://spinspire.com/article/project-recipes)._

_Note 2: These templates have features that you probably don't need or use. So remember trim down whatever you borrow. The goal is to avoid reinventing the wheel._

- `docker-compose`
  - `entrypoint.sh` script to initialize a container before use.
  - `traefik` reverse proxy `labels`, router rules, and `networks` provided so that your container can receive HTTP requests.
  - Main `docker-compose.yml` file + `.env` and `docker-compose.override.yml` files.
- `sk`: Svelte-Kit
  - Static frontend with `adapter-static`. No SSR. Can be turned on if needed.
  - Live Dev with HMR
  - `vite` proxy to the backend server
  - Svelte component testing route at /components (works standalone and can be pulled into the route folder of any sveltekit project)
- `pb`: PocketBase / Go
  - Live Dev with `modd`
  - Go type to TypeScript type generation with `tygo`
  - PocketBase record to TypeScript type generation with `pocketbase-typegen`
  - Serve static frontend using `--publicDir ../sk/build`
- `py`: Python / FastAPI
  - Mount Python routes to a configurable prefix (e.g. `/apy`)
- `mb`: Metabase

Coming soon ...

- `rs`: Rust
- `dr`: Drupal
- `ng`: Nginx
- `pg`: PostGres
- `my`: MySQL/MariaDB

Read the README files the respective folders to understand the details of a specific stack component.

# How to use

Basically use [`degit`](https://github.com/Rich-Harris/degit).

For example, use a specific template ...

- `npx degit spinspire/receipes/sk myprj/sk`
- `npx degit spinspire/receipes/pb myprj/pb`
- `npx degit spinspire/receipes/mb myprj/mb`
- `npx degit spinspire/receipes/py myprj/py`

Or the whole project ...

- `npx degit spinspire/receipes myprj`
