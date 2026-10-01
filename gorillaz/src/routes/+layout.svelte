<script>
	import '../app.css';
	import { resolve } from '$app/paths';
	import { browser } from '$app/environment';

	let { children } = $props();
	let theme = $state(browser ? (document.documentElement.dataset.theme ?? 'dark') : 'dark');

	function toggleTheme() {
		theme = theme === 'light' ? 'dark' : 'light';
		document.documentElement.dataset.theme = theme;
		try {
			localStorage.setItem('gorillaz:theme', theme);
		} catch {}
	}
</script>

<svelte:head>
	<title>Gorillaz collaborators – who worked with whom</title>
	<meta name="description" content="Every artist credited on a Gorillaz recording, and how they are connected to each other." />
</svelte:head>

<header>
	<a class="brand" href={resolve('/')}>
		<span class="logo">G</span>
		<span class="brand-text">
			<span class="brand-name">Gorillaz collaborators</span>
			<span class="brand-sub muted">who worked with whom</span>
		</span>
	</a>
	<nav>
		<a href={resolve('/')}>Graph</a>
		<a href={resolve('/artists')}>Artists</a>
		<a href={resolve('/about')}>About</a>
	</nav>
	<button class="chip" onclick={toggleTheme} aria-label="Toggle theme">{theme === 'light' ? '☾' : '☀'}</button>
</header>

<main>
	{@render children()}
</main>

<footer class="muted">
	<p>
		Data from <a href="https://musicbrainz.org/artist/e21857d5-3256-4547-afb3-4b6ded592596">MusicBrainz</a>, CC0.
		Part of <a href="https://sgugler.ch/">sgugler.ch</a>.
	</p>
</footer>

<style>
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
		padding: 0.6rem clamp(1rem, 3vw, 2rem);
		border-bottom: 1px solid var(--line);
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 0.7rem;
		text-decoration: none;
	}
	.logo {
		display: inline-grid;
		place-items: center;
		width: 2.2rem;
		height: 2.2rem;
		border-radius: 0.5rem;
		background: var(--accent);
		color: var(--accent-fg);
		font-weight: 900;
		font-size: 1.4rem;
	}
	.brand-text {
		display: flex;
		flex-direction: column;
		line-height: 1.15;
	}
	.brand-name {
		font-weight: 700;
	}
	.brand-sub {
		font-size: 0.8rem;
	}
	nav {
		display: flex;
		gap: 1rem;
	}
	nav a {
		text-decoration: none;
		color: var(--muted);
	}
	nav a:hover {
		color: var(--fg);
	}
	main {
		max-width: 1400px;
		margin: 0 auto;
		padding: 1rem clamp(1rem, 3vw, 2rem) 2rem;
	}
	footer {
		padding: 1rem clamp(1rem, 3vw, 2rem);
		font-size: 0.85rem;
		border-top: 1px solid var(--line);
	}
</style>
