<script>
	import { resolve } from '$app/paths';
	let { data } = $props();
	const a = $derived(data.artist);
</script>

<svelte:head>
	<title>{a.name} × Gorillaz</title>
</svelte:head>

<nav class="muted"><a href={resolve('/')}>← graph</a> · <a href={resolve('/artists')}>all artists</a></nav>

<h1><span class="dot" style:background={a.color}></span>{a.name}</h1>
<p class="muted">
	{[a.type, a.area, a.begin ? 'since ' + a.begin.slice(0, 4) : null, a.disambiguation].filter(Boolean).join(' · ')}
	{#if a.tags?.length}<br />{a.tags.join(', ')}{/if}
	<br />{#if a.wikipedia}<a href={a.wikipedia}>Wikipedia</a> · {/if}<a href="https://musicbrainz.org/artist/{a.id}">MusicBrainz</a>
</p>

<div class="grid">
	<section class="card">
		<h2>With Gorillaz · {a.era}</h2>
		<ol>
			{#each a.songs as s}<li>{s.title}{#if s.year}&nbsp;<span class="muted">{s.year}</span>{/if}{#if s.album}&nbsp;<span class="muted">({s.album})</span>{/if}</li>{/each}
		</ol>
	</section>
	<section class="card">
		<h2>Connections among Gorillaz collaborators</h2>
		{#if data.connections.length}
			<ul>
				{#each data.connections as c}
					<li>
						<a href={resolve('/artist/[id]', { id: c.other.id })}>{c.other.name}</a>
						<span class="muted">
							{#if c.kind === 'credit'}recorded together: {c.titles.join(', ')}{:else if c.kind === 'band'}{c.rel}{/if}
						</span>
					</li>
				{/each}
			</ul>
		{:else}
			<p class="muted">None recorded in MusicBrainz.</p>
		{/if}
	</section>
</div>

<style>
	nav {
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}
	h1 {
		margin: 0 0 0.25rem;
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}
	.dot {
		width: 1rem;
		height: 1rem;
		border-radius: 50%;
		display: inline-block;
	}
	h2 {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 0 0 0.6rem;
	}
	.grid {
		display: grid;
		gap: 1rem;
		grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr));
		margin-top: 1rem;
	}
	ol,
	ul {
		margin: 0;
		padding-left: 1.2rem;
	}
	li {
		margin-bottom: 0.2rem;
	}
</style>
