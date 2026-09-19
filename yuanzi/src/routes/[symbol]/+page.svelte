<script>
	import { resolve } from '$app/paths';
	import { radicals, origins } from '$lib/data.js';
	import Glyph from '$lib/Glyph.svelte';
	import History from '$lib/History.svelte';

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
			<a class="part" href={resolve('/phonetic/[char]', { char: e.phonetic })} title="All about the component {e.phonetic}">
				<span class="big hanzi">{e.phonetic}</span>
				<span class="label">{e.origin === 'property' ? 'sound and meaning' : 'phonetic'}{#if data.extras.matched !== null}<br />from
						{#each data.extras.syllables as s, i}<span class="syl" class:hit={i === data.extras.matched}>{s}</span>{/each}{/if}</span>
			</a>
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

<section class="card history">
	<h2>History of the character</h2>
	{#if data.history.forms.length}
		<p class="muted intro">
			Every form found in the sources, from the first missionary chemistry books of the 1850s to the current
			standards. Hover a dot for the source. Simplified <b class="hanzi">{data.history.current.hans}</b>, traditional
			<b class="hanzi">{data.history.current.hant}</b>{#if data.history.current.tw !== data.history.current.hant || data.history.current.twPinyin !== data.history.current.pinyin}, Taiwan
				<b class="hanzi">{data.history.current.tw}</b> <i>{data.history.current.twPinyin}</i>{/if}.
		</p>
		<History element={e} record={data.history} />
	{:else}
		<p class="muted">
			No earlier form is recorded in the sources consulted. Simplified <b class="hanzi">{data.history.current.hans}</b>,
			traditional <b class="hanzi">{data.history.current.hant}</b>{#if data.history.current.tw !== data.history.current.hant}, Taiwan
				<b class="hanzi">{data.history.current.tw}</b> <i>{data.history.current.twPinyin}</i>{/if}.
		</p>
	{/if}
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
		<h2>Elsewhere</h2>
		<p class="langs">
			{#if data.extras.ja}<span><b>Japanese</b> <span lang="ja">{data.extras.ja}</span></span>{/if}
			{#if data.extras.ko}<span><b>Korean</b> <span lang="ko">{data.extras.ko}</span></span>{/if}
			{#if data.extras.vi}<span><b>Vietnamese</b> <span lang="vi">{data.extras.vi}</span></span>{/if}
		</p>
		{#if data.extras.etymology}
			<p class="muted">
				Western name from {data.extras.etymology.language ? data.extras.etymology.language + ' ' : ''}<i>{data.extras.etymology.word}</i>{#if data.extras.etymology.meaning}, “{data.extras.etymology.meaning}”{/if}.
				<a href={resolve('/languages')}>Compare all</a>
			</p>
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
	.anatomy,
	.history {
		margin-bottom: 1rem;
	}
	.intro {
		margin-top: 0;
	}
	.equation {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	a.part {
		text-decoration: none;
		color: inherit;
	}
	a.part:hover {
		border-color: var(--accent);
	}
	.syl {
		color: var(--muted);
	}
	.syl.hit {
		color: var(--accent);
		font-weight: 700;
		text-decoration: underline;
	}
	.langs {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
		margin: 0 0 0.5rem;
	}
	.langs b {
		font-weight: 600;
		color: var(--muted);
		display: inline-block;
		width: 6.5rem;
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
