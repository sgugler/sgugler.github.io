<script>
	import { resolve } from '$app/paths';
	import { radicals, origins } from '$lib/data.js';
	import Glyph from '$lib/Glyph.svelte';

	let { data } = $props();
	const e = $derived(data.element);
	const rad = $derived(radicals[e.radicalKey]);

	function href(other) {
		return resolve('/[symbol]', { symbol: other.symbol.toLowerCase() });
	}
</script>

<svelte:head>
	<title>{e.char} {e.pinyin} – {e.name} ({e.symbol}) · 元字</title>
</svelte:head>

<nav class="crumbs muted">
	<a href={resolve('/')}>← all elements</a>
	<span class="spacer"></span>
	{#if data.prev}<a href={href(data.prev)}>‹ {data.prev.symbol}</a>{/if}
	{#if data.next}<a href={href(data.next)}>{data.next.symbol} ›</a>{/if}
</nav>

<article class="element">
	<div class="hero radical-{e.radicalKey}">
		<Glyph element={e} size="clamp(6rem, 22vw, 10rem)" />
	</div>
	<div class="summary">
		<h1>{e.name} <span class="muted">{e.symbol} · {e.z}</span></h1>
		<p class="pinyin">{e.pinyin}</p>
		<p class="muted">
			{rad.state} · period {e.period}{#if e.group !== null}, group {e.group}{/if} · {e.block}-block
		</p>
	</div>
</article>

<section class="card anatomy">
	<h2>Anatomy</h2>
	{#if e.phonetic}
		<div class="equation">
			<div class="part radical-{e.radicalKey}">
				<span class="big hanzi">{e.radical}</span>
				<span class="label">radical <b class="hanzi">{rad.full}</b> <i>{rad.pinyin}</i><br />{rad.meaning} → {rad.state}</span>
			</div>
			<span class="op">+</span>
			<div class="part">
				<span class="big hanzi">{e.phonetic}</span>
				<span class="label">{e.origin === 'property' ? 'sound and meaning' : 'phonetic'}</span>
			</div>
			<span class="op">=</span>
			<div class="part">
				<span class="big"><Glyph element={e} size="2.6rem" /></span>
				<span class="label"><i>{e.pinyin}</i></span>
			</div>
		</div>
	{:else}
		<p>
			<b class="hanzi">{e.char}</b> is the radical itself: <i>{rad.pinyin}</i>, “{rad.meaning}”. All other metal
			characters are built on it.
		</p>
	{/if}
	<p>
		<b>{origins[e.origin].label}.</b>
		{origins[e.origin].description}
		{#if e.note}<span class="note">{e.note}</span>{/if}
	</p>
</section>

<div class="grid">
	<section class="card">
		<h2>Homophones</h2>
		{#if data.homophones.same.length}
			<p>
				Sounds exactly like
				{#each data.homophones.same as o, i}{#if i}{', '}{/if}<a href={href(o)}><span class="hanzi">{o.char}</span> {o.name}</a>{/each}.
				Only the written radical tells them apart.
			</p>
		{/if}
		{#if data.homophones.toneOnly.length}
			<p>
				Same syllable, different tone:
				{#each data.homophones.toneOnly as o, i}{#if i}{', '}{/if}<a href={href(o)}><span class="hanzi">{o.char}</span> {o.pinyin} {o.name}</a>{/each}.
			</p>
		{/if}
		{#if !data.homophones.same.length && !data.homophones.toneOnly.length}
			<p class="muted">No other element shares this syllable.</p>
		{/if}
	</section>

	<section class="card">
		<h2>Unicode</h2>
		<p>
			<code>{e.codepoint}</code> in {e.unicodeBlock}
			{#if e.glyph}
				<span class="muted">(outside the Basic Multilingual Plane, so most fonts lack it; shown here from an outline)</span>
			{/if}
		</p>
		{#if e.discovered}<p class="muted">Element discovered {e.discovered}.</p>{/if}
	</section>
</div>

<style>
	.crumbs {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
		font-size: 0.95rem;
	}
	.spacer {
		flex: 1;
	}
	.element {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		flex-wrap: wrap;
		margin-bottom: 1.25rem;
	}
	.hero {
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 1rem;
		padding: 1.25rem;
		min-width: 10rem;
		min-height: 10rem;
	}
	h1 {
		margin: 0 0 0.25rem;
		font-size: clamp(1.6rem, 4vw, 2.4rem);
	}
	.pinyin {
		font-size: 1.6rem;
		margin: 0 0 0.25rem;
	}
	.summary p {
		margin: 0;
	}
	h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 0 0 0.75rem;
	}
	.anatomy {
		margin-bottom: 1rem;
	}
	.equation {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	.part {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.6rem 0.9rem;
		border-radius: 0.6rem;
		border: 1px solid var(--line);
	}
	.big {
		font-size: 2.6rem;
		line-height: 1;
	}
	.label {
		font-size: 0.85rem;
		line-height: 1.3;
	}
	.op {
		font-size: 1.6rem;
		color: var(--muted);
	}
	.note {
		display: block;
		margin-top: 0.4rem;
		color: var(--muted);
	}
	.grid {
		display: grid;
		gap: 1rem;
		grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
	}
	code {
		font-size: 0.95em;
	}
</style>
