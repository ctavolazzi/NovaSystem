<script>
	import '../app.postcss';
	import DiCode from 'svelte-icons/di/DiCode.svelte';
</script>

<div class="h-full w-full min-h-screen bg-base-200">
	<div class="bg-base-100 border-b-2">
		<div class="navbar xl:container mx-auto bg-base-100 px-4">
			<div class="navbar-start">
				<div class="dropdown">
					<button class="btn btn-ghost md:hidden">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 6h16M4 12h8m-8 6h16"
							/></svg
						>
					</button>
					<ul
						class="menu menu-compact dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52"
					>
						<li><a href="/login">Login</a></li>
						<li><a href="/register">Register</a></li>
					</ul>
				</div>
				<a
					href="/"
					class="h-12 w-12 text-xl  text-base-100 hover:cursor-pointer bg-primary rounded-md"
				>
					<DiCode />
				</a>
			</div>
			<div class="navbar-end space-x-2">
				<a href="/login" class="btn btn-outline">Login</a>
				<a href="/register" class="btn btn-primary btn-outline">Register</a>
			</div>
		</div>
	</div>
	<div class="h-full w-full xl:container mx-auto mt-8 px-4">
		<slot />
	</div>
</div>
