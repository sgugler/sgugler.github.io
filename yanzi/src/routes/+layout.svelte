<script>
	import '../app.css';
	import { resolve } from '$app/paths';
	import { browser } from '$app/environment';

	let { children } = $props();

	let theme = $state(browser ? (document.documentElement.dataset.theme ?? 'system') : 'system');

	function toggleTheme() {
		const dark = matchMedia('(prefers-color-scheme: dark)').matches;
		const current = theme === 'system' ? (dark ? 'dark' : 'light') : theme;
		theme = current === 'dark' ? 'light' : 'dark';
		document.documentElement.dataset.theme = theme;
		try {
			localStorage.setItem('yanzi:theme', theme);
		} catch {}
	}
</script>

<svelte:head>
	<title>元字 Yuánzì – Chinese characters of the chemical elements</title>
	<meta
		name="description"
		content="Search and explore the Chinese characters of all 118 chemical elements: radical, phonetic component, pinyin, origin and Unicode."
	/>
</svelte:head>

<header>
	<a class="brand" href={resolve('/')}>
		<span class="hanzi logo">元字</span>
		<span class="brand-text">
			<span class="brand-name">yuánzì</span>
			<span class="brand-sub">Chinese characters of the chemical elements</span>
		</span>
	</a>
	<button class="chip theme" onclick={toggleTheme} aria-label="Toggle light or dark theme" title="Light / dark">◐</button>
</header>

<main>
	{@render children()}
</main>

<footer class="muted">
	<p>
		Data from S. Gugler, Y. Cui, P. O. Dral,
		<a href="https://doi.org/10.1007/s40828-026-00222-0">Architecture of Chinese chemical element names</a>,
		<i>ChemTexts</i> 12, 11 (2026). Part of <a href="https://sgugler.ch/">sgugler.ch</a>.
	</p>
</footer>

<style>
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 1rem clamp(1rem, 4vw, 3rem);
		border-bottom: 1px solid var(--line);
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		text-decoration: none;
	}
	.logo {
		font-size: 2rem;
		font-weight: 700;
		color: var(--accent);
		line-height: 1;
	}
	.brand-text {
		display: flex;
		flex-direction: column;
		line-height: 1.2;
	}
	.brand-name {
		font-weight: 600;
	}
	.brand-sub {
		font-size: 0.85rem;
		color: var(--muted);
	}
	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1.5rem clamp(1rem, 4vw, 3rem) 3rem;
	}
	footer {
		padding: 1rem clamp(1rem, 4vw, 3rem) 2rem;
		font-size: 0.85rem;
		border-top: 1px solid var(--line);
	}
</style>
