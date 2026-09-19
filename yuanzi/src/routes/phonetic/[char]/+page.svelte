<script>
	import { resolve } from '$app/paths';
	import { radicals, bySymbol } from '$lib/data.js';
	import Glyph from '$lib/Glyph.svelte';

	let { data } = $props();
	const p = $derived(data.phonetic);

	function href(e) {
		return resolve('/[symbol]', { symbol: e.symbol.toLowerCase() });
	}
	function plain(s) {
		return (s ?? '')
			.normalize('NFD')
			.replace(/[̀-ͯ]/g, '')
			.replace(/ü/g, 'u');
	}
	function verdict(e) {
		const r = (p.reading ?? '').split(' ')[0];
		if (e.pinyin === r) return 'The element keeps the component’s reading exactly.';
		if (plain(e.pinyin) === plain(r)) return `Same syllable, different tone: ${r} became ${e.pinyin}.`;
		return `The reading drifted: the component is read ${r}, the element ${e.pinyin}.`;
	}
</script>

<svelte:head>
	<title>{p.char} {p.reading ?? ''} – phonetic component · 元字</title>
</svelte:head>

<nav class="crumbs muted"><a href={resolve('/phonetic')}>← all phonetic components</a></nav>

<article class="head">
	<span class="hanzi big">{p.char}</span>
	<div>
		<h1>{p.char} <span class="muted"><i>{p.reading ?? 'reading unknown'}</i></span></h1>
		{#if p.definition}<p class="def">“{p.definition}”</p>{/if}
		<p class="muted small">
			On its own, an ordinary character{#if p.cantonese}; Cantonese {p.cantonese}{/if}. Readings and gloss from the
			Unicode Unihan database.
		</p>
	</div>
</article>

{#each p.elements as e}
	{@const full = bySymbol.get(e.symbol.toLowerCase())}
	<section class="card">
		<h2>Carries <a href={href(e)}>{e.name}</a></h2>
		<div class="equation">
			<div class="part radical-{full.radicalKey}">
				<span class="big2 hanzi">{full.radical}</span>
				<span class="label">{radicals[full.radicalKey].meaning} → {radicals[full.radicalKey].state}</span>
			</div>
			<span class="op">+</span>
			<div class="part">
				<span class="big2 hanzi">{p.char}</span>
				<span class="label"><i>{p.reading ?? ''}</i></span>
			</div>
			<span class="op">=</span>
			<div class="part">
				<a class="big2" href={href(e)}><Glyph element={e} size="2.6rem" /></a>
				<span class="label"><i>{e.pinyin}</i> · {e.symbol} {e.z}</span>
			</div>
		</div>
		{#if e.matched !== null}
			<p>
				Transliterates syllable {e.matched + 1} of <b>{e.syllables.join('·')}</b>:
				{#each e.syllables as s, i}<span class:hit={i === e.matched} class="syl">{s}</span>{/each}
				→ <i>{e.pinyin}</i>.
			</p>
		{:else}
			<p>Not a plain transliteration: the component was chosen for its meaning, or the name is older than the system.</p>
		{/if}
		<p class="muted">{verdict(e)}</p>
	</section>
{/each}

{#if data.soundAlikes.length}
	<section class="card">
		<h2>Other elements read {(p.reading ?? '').split(' ')[0]}</h2>
		<p>
			{#each data.soundAlikes as e, i}{#if i}{', '}{/if}<a href={href(e)}><span class="hanzi">{e.char}</span> {e.name}</a>{/each}
		</p>
	</section>
{/if}

<style>
	.crumbs {
		margin-bottom: 1rem;
		font-size: 0.95rem;
	}
	.head {
		display: flex;
		gap: 1.5rem;
		align-items: center;
		margin-bottom: 1.25rem;
		flex-wrap: wrap;
	}
	.big {
		font-size: clamp(5rem, 18vw, 8rem);
		line-height: 1;
	}
	h1 {
		margin: 0 0 0.25rem;
	}
	.def {
		font-size: 1.15rem;
		margin: 0 0 0.25rem;
	}
	.small {
		font-size: 0.85rem;
		margin: 0;
	}
	h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 0 0 0.75rem;
	}
	h2 a {
		color: inherit;
	}
	.card {
		margin-bottom: 1rem;
	}
	.equation {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}
	.part {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.6rem 0.9rem;
		border-radius: 0.6rem;
		border: 1px solid var(--line);
	}
	.big2 {
		font-size: 2.6rem;
		line-height: 1;
	}
	.label {
		font-size: 0.85rem;
	}
	.op {
		font-size: 1.6rem;
		color: var(--muted);
	}
	.syl {
		padding: 0 0.1rem;
		color: var(--muted);
	}
	.syl.hit {
		color: var(--accent);
		font-weight: 700;
		text-decoration: underline;
	}
</style>
