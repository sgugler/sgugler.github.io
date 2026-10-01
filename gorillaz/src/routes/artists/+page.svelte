<script>
	import { resolve } from '$app/paths';
	import { artists, graph } from '$lib/data.js';
	let query = $state('');
	let era = $state(null);
	const list = $derived(
		artists.filter((a) => (!era || a.era === era) && (!query.trim() || a.name.toLowerCase().includes(query.trim().toLowerCase())))
	);
</script>

<svelte:head><title>All collaborators – Gorillaz</title></svelte:head>

<h1>{artists.length} collaborators</h1>
<div class="controls">
	<input type="search" bind:value={query} placeholder="Filter" aria-label="Filter artists" />
	<div class="chips">
		<button class="chip" aria-pressed={era === null} onclick={() => (era = null)}>all eras</button>
		{#each graph.eras as e}
			<button class="chip" aria-pressed={era === e.name} onclick={() => (era = era === e.name ? null : e.name)}><span class="dot" style:background={e.color}></span>{e.name}</button>
		{/each}
	</div>
</div>
<ul class="list">
	{#each list as a (a.id)}
		<li class="card">
			<a href={resolve('/artist/[id]', { id: a.id })}><span class="dot" style:background={a.color}></span>{a.name}</a>
			<span class="muted">{a.songs.length} track{a.songs.length === 1 ? '' : 's'}{#if a.first} · {a.first}{/if}{#if a.degree > 1} · {a.degree - 1} link{a.degree === 2 ? '' : 's'}{/if}</span>
			<span class="muted songs">{a.songs.slice(0, 3).map((s) => s.title).join(' · ')}</span>
		</li>
	{/each}
</ul>

<style>
	h1 {
		margin: 0 0 0.75rem;
	}
	.controls {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	input[type='search'] {
		max-width: 24rem;
		padding: 0.5rem 0.9rem;
		border: 1px solid var(--line);
		border-radius: 0.6rem;
		background: var(--card);
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.dot {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		margin-right: 0.4rem;
		vertical-align: middle;
	}
	.list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.5rem;
		grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
	}
	.list li {
		display: flex;
		flex-direction: column;
		padding: 0.7rem 0.9rem;
		font-size: 0.95rem;
	}
	.songs {
		font-size: 0.8rem;
	}
</style>
