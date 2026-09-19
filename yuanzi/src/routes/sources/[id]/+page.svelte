<script>
	import { resolve } from '$app/paths';
	import Glyph from '$lib/Glyph.svelte';
	let { data } = $props();
	const s = $derived(data.source);
	function href(e) {
		return resolve('/[symbol]', { symbol: e.symbol.toLowerCase() });
	}
</script>

<svelte:head>
	<title>{s.zh} {s.label} · 元字</title>
</svelte:head>

<nav class="crumbs muted"><a href={resolve('/sources')}>← all sources</a></nav>

<h1><span class="hanzi">{s.zh}</span> <span class="muted">{s.label}{#if s.year}, {s.year}{/if}</span></h1>
<p class="who">{s.who}</p>
{#if s.about}<p class="about">{s.about}</p>{/if}
{#if s.url}
	<p><a href={s.url}>{s.scan ?? 'Digitised copy'} ↗</a></p>
{/if}

{#if data.rows.length}
	<h2>Forms attested here ({data.rows.length})</h2>
	<ul class="rows">
		{#each data.rows as r}
			<li class="card" class:survives={r.survives}>
				<span class="hanzi form" title={r.ids ? `composition ${r.ids}` : ''}>{r.form}{#if r.ids}<small class="ids">{[...r.ids].filter((c) => !/[\u2FF0-\u2FFF]/.test(c)).join(' + ')}</small>{/if}</span>
				<span class="info">
					<a href={href(r.element)}>{r.element.name} {r.element.symbol}</a>
					{#if r.reading}<i class="muted"> {r.reading}</i>{/if}
					<span class="today muted">today <Glyph element={r.element} size="1.1rem" /> {r.element.pinyin}</span>
					{#if r.note}<span class="note muted">{r.note}</span>{/if}
				</span>
				<span class="tag" title={r.survives ? 'still a current form' : 'replaced'}>{r.survives ? 'survives' : 'replaced'}</span>
			</li>
		{/each}
	</ul>
{:else}
	<p class="muted">No individual forms are attributed to this source in the data yet.</p>
{/if}

<style>
	.crumbs {
		margin-bottom: 1rem;
		font-size: 0.95rem;
	}
	h1 {
		margin: 0 0 0.25rem;
	}
	.who {
		margin: 0 0 0.75rem;
	}
	.about {
		max-width: 62ch;
	}
	h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 1.5rem 0 0.75rem;
	}
	.rows {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.5rem;
		grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
	}
	.rows li {
		display: grid;
		grid-template-columns: auto 1fr auto;
		gap: 0.75rem;
		align-items: start;
		padding: 0.6rem 0.9rem;
	}
	.form {
		font-size: 1.8rem;
		line-height: 1.1;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.ids {
		font-size: 0.65rem;
		color: var(--muted);
	}
	.info {
		display: flex;
		flex-direction: column;
		font-size: 0.9rem;
	}
	.today,
	.note {
		font-size: 0.8rem;
	}
	.tag {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
	}
	.survives .tag {
		color: var(--accent);
	}
</style>
