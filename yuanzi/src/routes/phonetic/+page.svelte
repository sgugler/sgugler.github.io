<script>
	import { resolve } from '$app/paths';
	import phonetics from '$lib/phonetics.json';
	import Glyph from '$lib/Glyph.svelte';

	let query = $state('');
	let order = $state('z');

	const all = Object.values(phonetics);
	const list = $derived.by(() => {
		const q = query.trim().toLowerCase();
		let rows = all.filter(
			(p) =>
				!q ||
				p.char.includes(q) ||
				(p.reading ?? '').toLowerCase().includes(q) ||
				(p.definition ?? '').toLowerCase().includes(q) ||
				p.elements.some((e) => e.name.toLowerCase().includes(q) || e.symbol.toLowerCase() === q)
		);
		if (order === 'reading') rows = [...rows].sort((a, b) => (a.reading ?? '').localeCompare(b.reading ?? ''));
		else rows = [...rows].sort((a, b) => a.elements[0].z - b.elements[0].z);
		return rows;
	});

	function drift(p) {
		// does the element's reading keep the phonetic's reading?
		const r = (p.reading ?? '').split(' ')[0];
		return p.elements.map((e) => (e.pinyin === r ? 'same' : plain(e.pinyin) === plain(r) ? 'tone' : 'other'));
	}
	function plain(s) {
		return (s ?? '')
			.normalize('NFD')
			.replace(/[̀-ͯ]/g, '')
			.replace(/ü/g, 'u');
	}
</script>

<svelte:head>
	<title>Phonetic components · 元字</title>
</svelte:head>

<h1>Phonetic components</h1>
<p class="lead">
	The right-hand half of an element character is an ordinary character borrowed for its sound. Here are all
	{all.length} of them: what they mean on their own, how they are read, and which element each one carries.
	Most transliterate the first syllable of the international name, a few take the second (<span class="hanzi">铝</span> from
	a<b>lu</b>minium) or the third (<span class="hanzi">碘</span> from io<b>dine</b>).
</p>

<div class="controls">
	<input type="search" bind:value={query} placeholder="Search a component, reading, meaning or element" aria-label="Search phonetic components" />
	<div class="chips">
		<button class="chip" aria-pressed={order === 'z'} onclick={() => (order = 'z')}>by element</button>
		<button class="chip" aria-pressed={order === 'reading'} onclick={() => (order = 'reading')}>by reading</button>
	</div>
</div>

<ul class="grid">
	{#each list as p (p.char)}
		{@const d = drift(p)}
		<li>
			<a class="card item" href={resolve('/phonetic/[char]', { char: p.char })}>
				<span class="ph hanzi">{p.char}</span>
				<span class="info">
					<span class="reading"><i>{p.reading ?? '—'}</i></span>
					<span class="def muted">{p.definition ?? ''}</span>
				</span>
				<span class="els">
					{#each p.elements as e, i}
						<span class="el" title="{e.name}: reading {d[i] === 'same' ? 'kept' : d[i] === 'tone' ? 'changed tone' : 'changed'}">
							<Glyph element={e} size="1.5rem" /> <small>{e.symbol} <i>{e.pinyin}</i></small>
						</span>
					{/each}
				</span>
			</a>
		</li>
	{/each}
</ul>

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.lead {
		max-width: 60ch;
		margin: 0 0 1rem;
	}
	.controls {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	input[type='search'] {
		width: 100%;
		padding: 0.6rem 1rem;
		font-size: 1rem;
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		background: var(--card);
	}
	.chips {
		display: flex;
		gap: 0.4rem;
	}
	.grid {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.6rem;
		grid-template-columns: repeat(auto-fill, minmax(17rem, 1fr));
	}
	.item {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.3rem 0.9rem;
		text-decoration: none;
		height: 100%;
		padding: 0.8rem 1rem;
	}
	.ph {
		font-size: 2.6rem;
		line-height: 1;
		grid-row: 1 / span 2;
	}
	.info {
		display: flex;
		flex-direction: column;
		font-size: 0.9rem;
	}
	.def {
		font-size: 0.8rem;
		line-height: 1.25;
	}
	.els {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
		align-items: center;
	}
	.el {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
	}
</style>
