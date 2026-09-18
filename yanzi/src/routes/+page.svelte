<script>
	import { resolve } from '$app/paths';
	import { elements, radicals, origins, search } from '$lib/data.js';
	import Glyph from '$lib/Glyph.svelte';

	let query = $state('');
	let radical = $state(null);
	let origin = $state(null);
	let view = $state('table');

	const filtering = $derived(query.trim() !== '' || radical !== null || origin !== null);
	const results = $derived(search(query, radical, origin));
	const hits = $derived(new Set(results.map((e) => e.z)));

	// Grid placement: 18 groups across, periods 1-7, then the f-block rows.
	function cell(e) {
		if (e.group !== null) return { col: e.group, row: e.period };
		const start = e.period === 6 ? 57 : 89;
		return { col: e.z - start + 3, row: e.period + 3 };
	}

	function href(e) {
		return resolve('/[symbol]', { symbol: e.symbol.toLowerCase() });
	}
</script>

<section class="controls">
	<input
		type="search"
		bind:value={query}
		placeholder="Search: 铁, tie, Fe, iron, 26, 失 …"
		aria-label="Search elements"
		autocomplete="off"
	/>
	<div class="chips" role="group" aria-label="Filter by radical">
		<button class="chip" aria-pressed={radical === null} onclick={() => (radical = null)}>all radicals</button>
		{#each Object.entries(radicals) as [key, r]}
			<button class="chip" aria-pressed={radical === key} onclick={() => (radical = radical === key ? null : key)}>
				<span class="hanzi">{r.char}</span> {r.state}
			</button>
		{/each}
	</div>
	<div class="chips" role="group" aria-label="Filter by origin">
		{#each Object.entries(origins) as [key, o]}
			<button class="chip" aria-pressed={origin === key} onclick={() => (origin = origin === key ? null : key)}>
				{o.label}
			</button>
		{/each}
		<span class="spacer"></span>
		<button class="chip" aria-pressed={view === 'table'} onclick={() => (view = 'table')}>table</button>
		<button class="chip" aria-pressed={view === 'list'} onclick={() => (view = 'list')}>list</button>
	</div>
	<p class="muted count">
		{#if filtering}{results.length} of {elements.length} elements{:else}{elements.length} elements. Click one for its anatomy.{/if}
	</p>
</section>

{#if view === 'table'}
	<div class="table-wrap">
		<div class="table" style:--cols={18}>
			{#each elements as e (e.z)}
				{@const c = cell(e)}
				<a
					class="el radical-{e.radicalKey}"
					class:dim={filtering && !hits.has(e.z)}
					href={href(e)}
					style:grid-column={c.col}
					style:grid-row={c.row}
					title="{e.name} ({e.symbol})"
				>
					<span class="z">{e.z}</span>
					<span class="ch"><Glyph element={e} size="1.6rem" /></span>
					<span class="sym">{e.symbol}</span>
					<span class="py">{e.pinyin}</span>
				</a>
			{/each}
			<div class="el placeholder" style:grid-column={3} style:grid-row={6}>57–71</div>
			<div class="el placeholder" style:grid-column={3} style:grid-row={7}>89–103</div>
		</div>
	</div>
{:else}
	<ul class="list">
		{#each results as e (e.z)}
			<li>
				<a href={href(e)} class="row">
					<span class="swatch radical-{e.radicalKey}"><Glyph element={e} size="1.8rem" /></span>
					<span class="row-main">
						<b>{e.name}</b> <span class="muted">{e.symbol} · {e.z}</span>
						<br />
						<span>{e.pinyin}</span>
						{#if e.phonetic}<span class="muted"> · {e.radical} + <span class="hanzi">{e.phonetic}</span></span>{/if}
					</span>
					<span class="muted origin">{origins[e.origin].label}</span>
				</a>
			</li>
		{:else}
			<li class="muted">Nothing matches.</li>
		{/each}
	</ul>
{/if}

<section class="legend card">
	<p>
		Every modern element character is a phono-semantic compound: a <b>radical</b> on the left gives the state at room
		temperature, a <b>phonetic</b> on the right hints at the sound. Four radicals cover the whole table:
	</p>
	<ul class="legend-list">
		{#each Object.entries(radicals) as [key, r]}
			<li>
				<span class="swatch radical-{key}"><span class="hanzi">{r.char}</span></span>
				<span><b class="hanzi">{r.full}</b> <i>{r.pinyin}</i>, “{r.meaning}” — {r.state}</span>
			</li>
		{/each}
	</ul>
</section>

<style>
	.controls {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
		margin-bottom: 1.25rem;
	}
	input[type='search'] {
		width: 100%;
		padding: 0.7rem 1rem;
		font-size: 1.1rem;
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		background: var(--card);
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		align-items: center;
	}
	.spacer {
		flex: 1;
	}
	.count {
		margin: 0;
		font-size: 0.9rem;
	}
	.table-wrap {
		overflow-x: auto;
		padding-bottom: 0.5rem;
	}
	.table {
		display: grid;
		grid-template-columns: repeat(var(--cols), minmax(3.4rem, 1fr));
		grid-auto-rows: auto;
		gap: 3px;
		min-width: 64rem;
	}
	.table :global(.el:nth-child(n)) {
		min-width: 0;
	}
	.el {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.05rem;
		padding: 0.3rem 0.1rem;
		border-radius: 0.35rem;
		text-decoration: none;
		color: var(--fg);
		font-size: 0.7rem;
		line-height: 1.15;
		transition: opacity 0.15s, transform 0.1s;
	}
	.el:hover {
		transform: scale(1.06);
		outline: 2px solid var(--accent);
	}
	.el.dim {
		opacity: 0.18;
	}
	.el .z {
		align-self: flex-start;
		font-size: 0.6rem;
		color: var(--muted);
		margin-left: 0.2rem;
		margin-bottom: -0.4rem;
	}
	.el .sym {
		font-weight: 700;
	}
	.el .py {
		color: var(--muted);
	}
	.placeholder {
		color: var(--muted);
		border: 1px dashed var(--line);
	}
	/* space between the main table and the f-block */
	.table :global(.el[style*='grid-row: 9']) {
		margin-top: 0.6rem;
	}
	.list {
		list-style: none;
		padding: 0;
		margin: 0 0 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}
	.row {
		display: flex;
		align-items: center;
		gap: 0.9rem;
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--line);
		border-radius: 0.6rem;
		background: var(--card);
		text-decoration: none;
	}
	.row-main {
		flex: 1;
	}
	.origin {
		font-size: 0.85rem;
	}
	.swatch {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 3rem;
		height: 3rem;
		border-radius: 0.5rem;
		flex-shrink: 0;
	}
	.legend {
		margin-top: 1.5rem;
	}
	.legend p {
		margin-top: 0;
	}
	.legend-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.6rem;
		grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
	}
	.legend-list li {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	.legend-list .swatch {
		width: 2.4rem;
		height: 2.4rem;
		font-size: 1.3rem;
	}
</style>
