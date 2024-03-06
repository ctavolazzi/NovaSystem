<script>
	export let name;
	import Viewport from './components/Viewport.svelte';
	let content = "Welcome to NovaSystem!";
</script>

<main>
	<Viewport {content} />
	<h1>Hello {name}!</h1>
	<p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>
	<p>Welcome to the Dockerized NovaSystem application.</p>
	<p>Please fork and develop from this template.</p>
	<p>Remember to use the following commands:</p>
	<p>npm install</p>
	<p>npm run dev</p>
	<p>docker-compose up --build</p>
	<p>If you understand the structure and get this working, please feel compelled to make changes and then make a PR to the main NovaSystem repository, located <a href="https://www.github.com/ctavolazzi/NovaSystem
		">here: NovaSystem GitHub</a></p>
	<p>Good luck!</p>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>