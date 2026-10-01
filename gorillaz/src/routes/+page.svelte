<script>
	import { resolve } from '$app/paths';
	import { graph, byId, connections, GID } from '$lib/data.js';
	import Graph from '$lib/Graph.svelte';

	let selected = $state(null);
	let query = $state('');
	let kinds = $state(new Set(['feature', 'credit', 'band']));

	const sel = $derived(selected ? byId.get(selected) : null);
	const conns = $derived(selected ? connections(selected).filter((c) => c.other.id !== GID) : []);

	function toggle(k) {
		const s = new Set(kinds);
		s.has(k) ? s.delete(k) : s.add(k);
		kinds = s;
	}
	const counts = $derived({
		feature: graph.edges.filter((e) => e.kind === 'feature').length,
		credit: graph.edges.filter((e) => e.kind === 'credit').length,
		band: graph.edges.filter((e) => e.kind === 'band').length
	});
</script>

<section class="controls">
	<input type="search" bind:value={query} placeholder="Find an artist" aria-label="Find an artist" />
	<div class="chips">
		<button class="chip" aria-pressed={kinds.has('feature')} onclick={() => toggle('feature')}>
			<span class="sw feature"></span> featured with Gorillaz ({counts.feature})
		</button>
		<button class="chip" aria-pressed={kinds.has('credit')} onclick={() => toggle('credit')}>
			<span class="sw credit"></span> recorded together elsewhere ({counts.credit})
		</button>
		<button class="chip" aria-pressed={kinds.has('band')} onclick={() => toggle('band')}>
			<span class="sw band"></span> same band ({counts.band})
		</button>
	</div>
	<div class="eras">
		{#each graph.eras as e}<span class="era"><span class="dot" style:background={e.color}></span>{e.name}</span>{/each}
	</div>
</section>

<div class="layout" class:open={!!sel}>
	<div class="graph" onclick={() => (selected = null)} role="presentation">
		<Graph {graph} {selected} {kinds} {query} onselect={(id) => (selected = id)} />
	</div>
	{#if sel}
		<aside class="card panel">
			<h2><a href={resolve('/artist/[id]', { id: sel.id })}>{sel.name}</a></h2>
			<p class="muted small">
				{sel.type ?? ''}{#if sel.area} · {sel.area}{/if}{#if sel.first} · first with Gorillaz {sel.first}{/if}
				{#if sel.tags?.length}<br />{sel.tags.slice(0, 4).join(', ')}{/if}
			</p>
			{#if sel.songs.length}
				<h3>With Gorillaz</h3>
				<ul>
					{#each sel.songs.slice(0, 8) as s}<li>{s.title}{#if s.year}&nbsp;<span class="muted">{s.year}</span>{/if}</li>{/each}
					{#if sel.songs.length > 8}<li class="muted">and {sel.songs.length - 8} more</li>{/if}
				</ul>
			{/if}
			{#if conns.length}
				<h3>Connected to</h3>
				<ul>
					{#each conns.slice(0, 12) as c}
						<li>
							<button class="linkish" onclick={() => (selected = c.other.id)}>{c.other.name}</button>
							<span class="muted small">
								{#if c.kind === 'credit'}on {c.titles.slice(0, 2).join(', ')}{:else if c.kind === 'band'}{c.rel}{/if}
							</span>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="muted small">No recorded link to other Gorillaz collaborators in MusicBrainz.</p>
			{/if}
			<p><a href={resolve('/artist/[id]', { id: sel.id })}>Full page →</a></p>
		</aside>
	{/if}
</div>

<p class="muted hint">Drag to pan, scroll to zoom, click an artist to see their links. Node size is the number of Gorillaz tracks; colour is the era of their first one.</p>

<style>
	.controls {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}
	input[type='search'] {
		width: 100%;
		max-width: 28rem;
		padding: 0.55rem 0.9rem;
		border: 1px solid var(--line);
		border-radius: 0.6rem;
		background: var(--card);
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.sw {
		display: inline-block;
		width: 1.1rem;
		height: 0;
		border-top: 2px solid var(--muted);
		vertical-align: middle;
		margin-right: 0.3rem;
	}
	.sw.credit {
		border-color: var(--accent);
	}
	.sw.band {
		border-color: #ff6fb5;
		border-top-style: dashed;
	}
	.chip[aria-pressed='true'] .sw.credit {
		border-color: var(--accent-fg);
	}
	.eras {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem 0.9rem;
		font-size: 0.8rem;
		color: var(--muted);
	}
	.dot {
		display: inline-block;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		margin-right: 0.3rem;
		vertical-align: middle;
	}
	.layout {
		display: grid;
		grid-template-columns: 1fr;
		gap: 1rem;
	}
	.layout.open {
		grid-template-columns: 1fr minmax(16rem, 20rem);
	}
	.panel h2 {
		margin: 0 0 0.25rem;
		font-size: 1.25rem;
	}
	.panel h3 {
		margin: 0.9rem 0 0.3rem;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}
	.panel ul {
		margin: 0;
		padding-left: 1.1rem;
	}
	.small {
		font-size: 0.85rem;
	}
	.linkish {
		background: none;
		border: 0;
		padding: 0;
		text-decoration: underline;
		cursor: pointer;
	}
	.hint {
		font-size: 0.85rem;
		margin-top: 0.75rem;
	}
	@media (max-width: 800px) {
		.layout.open {
			grid-template-columns: 1fr;
		}
	}
</style>
