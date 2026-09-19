<script>
	import { resolve } from '$app/paths';
	import { elements } from '$lib/data.js';
	import extras from '$lib/extras.json';
	import history from '$lib/history.json';
	import Glyph from '$lib/Glyph.svelte';

	let query = $state('');
	const rows = $derived(
		elements.filter((e) => {
			const q = query.trim().toLowerCase();
			if (!q) return true;
			const x = extras[e.symbol];
			return [e.name, e.symbol, e.char, e.pinyin, x.ja, x.ko, x.vi, x.etymology?.word, x.etymology?.meaning, x.etymology?.language]
				.filter(Boolean)
				.some((s) => String(s).toLowerCase().includes(q));
		})
	);
	function href(e) {
		return resolve('/[symbol]', { symbol: e.symbol.toLowerCase() });
	}
</script>

<svelte:head>
	<title>Names across languages · 元字</title>
</svelte:head>

<h1>The same elements, four scripts</h1>
<p class="lead">
	Japanese usually transliterates in katakana but glosses the classical gases with 素 “element”: 水素 water-element for
	hydrogen where Chinese has 氫 light-gas, 酸素 acid-element for oxygen where Chinese has 氧 nourishing. Korean reads
	the Japanese compounds in Sino-Korean (수소, 산소) and otherwise borrows from English or German. Vietnamese keeps
	old Chinese loans for the ancient metals (đồng from 銅, thiếc from 錫) and clips French for the rest. The last column
	gives the Western etymology the Chinese phonetic was chosen to echo.
</p>

<input type="search" bind:value={query} placeholder="Filter by any name, script or meaning" aria-label="Filter" />

<div class="wrap">
	<table>
		<thead>
			<tr>
				<th>Z</th>
				<th>Element</th>
				<th>Chinese</th>
				<th>Taiwan</th>
				<th>Japanese</th>
				<th>Korean</th>
				<th>Vietnamese</th>
				<th>Origin of the Western name</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as e (e.z)}
				{@const x = extras[e.symbol]}
				{@const cur = history[e.symbol].current}
				<tr>
					<td class="num">{e.z}</td>
					<td><a href={href(e)}>{e.name}</a> <span class="muted">{e.symbol}</span></td>
					<td class="hanzi"><Glyph element={e} size="1.3rem" /> <small>{e.pinyin}</small></td>
					<td class="hanzi">{#if cur.tw !== cur.hant || cur.twPinyin !== e.pinyin}{cur.tw} <small>{cur.twPinyin}</small>{:else}<span class="muted">—</span>{/if}</td>
					<td lang="ja">{x.ja ?? ''}</td>
					<td lang="ko">{x.ko ?? ''}</td>
					<td lang="vi">{x.vi ?? ''}</td>
					<td class="etym">
						{#if x.etymology}
							<span>{x.etymology.word}</span>
							{#if x.etymology.meaning}<span class="muted"> “{x.etymology.meaning}”</span>{/if}
							{#if x.etymology.language}<span class="muted lang"> · {x.etymology.language}</span>{/if}
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.lead {
		max-width: 70ch;
		margin: 0 0 1rem;
	}
	input[type='search'] {
		width: 100%;
		padding: 0.6rem 1rem;
		font-size: 1rem;
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		background: var(--card);
		margin-bottom: 1rem;
	}
	.wrap {
		overflow-x: auto;
	}
	table {
		border-collapse: collapse;
		width: 100%;
		font-size: 0.92rem;
		min-width: 60rem;
	}
	th,
	td {
		text-align: left;
		padding: 0.4rem 0.6rem;
		border-bottom: 1px solid var(--line);
		vertical-align: top;
	}
	th {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
	}
	.num {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.hanzi {
		font-size: 1.1rem;
	}
	.etym {
		max-width: 28rem;
	}
	.lang {
		font-size: 0.8rem;
	}
</style>
