<script>
	// Timeline of every attested Chinese form of one element: each distinct
	// form is a row, time runs left to right, a bar spans the years a form is
	// attested, and dashed links show where a source replaced one form by another.
	import sources from './sources.json';
	import Glyph from './Glyph.svelte';

	/** @type {{ element: any, record: any }} */
	let { element, record } = $props();

	const Y0 = 1845;
	const Y1 = 2020;
	const W = 720;
	const LEFT = 132; // room for the form labels
	const RIGHT = 80; // room for "today"
	const ROW = 44;

	function x(year) {
		if (year === 0) return LEFT + 8; // antiquity
		if (year >= 9999) return W - RIGHT + 30; // today
		const t = (Math.min(Math.max(year, Y0), Y1) - Y0) / (Y1 - Y0);
		return LEFT + 40 + t * (W - LEFT - RIGHT - 70);
	}

	const rows = $derived.by(() => {
		const byForm = new Map();
		for (const a of record.forms) {
			if (!byForm.has(a.form)) byForm.set(a.form, { form: a.form, ids: a.ids, attestations: [] });
			const r = byForm.get(a.form);
			r.attestations.push(a);
			if (a.ids) r.ids = a.ids;
		}
		const current = record.current;
		const currentForms = new Set([current.hans, current.hant, current.tw]);
		const list = [...byForm.values()].map((r) => {
			const years = r.attestations.map((a) => a.year);
			r.first = Math.min(...years);
			r.last = Math.max(...years);
			r.isCurrent = currentForms.has(r.form);
			r.reading = r.attestations.find((a) => a.reading)?.reading;
			r.replaced = record.forms.some((o) => o.succeeds === r.form);
			return r;
		});
		// The form in use today always gets a row, even without attestations.
		if (!list.some((r) => r.isCurrent)) {
			list.push({ form: current.hant, attestations: [], first: 9999, last: 9999, isCurrent: true, reading: current.pinyin });
		}
		list.sort((a, b) => a.first - b.first || (a.isCurrent ? 1 : 0) - (b.isCurrent ? 1 : 0));
		return list;
	});

	const links = $derived(
		record.forms
			.filter((a) => a.succeeds)
			.map((a) => {
				const from = rows.findIndex((r) => r.form === a.succeeds);
				const to = rows.findIndex((r) => r.form === a.form);
				// start where the old form was last attested, end where the new one begins
				const x1 = from >= 0 ? Math.min(x(rows[from].last), x(a.year)) : 0;
				return { from, to, x1, x2: x(a.year) };
			})
			.filter((l) => l.from >= 0 && l.to >= 0)
	);

	/** "⿰金罕" → "金 + 罕", "⿱信金" → "信 over 金" for readers without IDS glyphs. */
	function composition(ids) {
		if (!ids) return '';
		const parts = [...ids].filter((c) => !/[⿰-⿿]/.test(c));
		return ids.startsWith('⿱') ? `${parts[0]} over ${parts[1]}` : parts.join(' + ');
	}

	const height = $derived(rows.length * ROW + 50);
	const ticks = [1850, 1875, 1900, 1925, 1950, 1975, 2000];

	function label(a) {
		const s = sources[a.source];
		return `${s.zh} · ${s.label}${s.year ? ` (${s.year})` : ''} — ${s.who}${a.note ? `\n${a.note}` : ''}`;
	}

	function yearText(y) {
		if (y === 0) return 'antiquity';
		if (y >= 9999) return 'today';
		return String(y);
	}
</script>

<div class="wrap">
	<svg viewBox="0 0 {W} {height}" width="100%" style:min-width="560px" role="img" aria-label="History of the character for {element.name}">
		<!-- axis -->
		{#each ticks as t}
			<line x1={x(t)} x2={x(t)} y1="18" y2={height - 24} class="grid" />
			<text x={x(t)} y="12" class="tick">{t}</text>
		{/each}
		<text x={x(0)} y="12" class="tick">antiquity</text>
		<text x={x(9999)} y="12" class="tick">today</text>

		<!-- succession links -->
		{#each links as l}
			{@const y1 = 30 + l.from * ROW + ROW / 2}
			{@const y2 = 30 + l.to * ROW + ROW / 2}
			<path d="M {l.x1} {y1} C {l.x1 + (l.x2 - l.x1) * 0.6} {y1}, {l.x2 - (l.x2 - l.x1) * 0.6} {y2}, {l.x2} {y2}" class="link" />
		{/each}

		{#each rows as r, i}
			{@const y = 30 + i * ROW + ROW / 2}
			{@const x1 = x(r.first)}
			{@const x2 = r.isCurrent ? x(9999) : x(r.last)}
			<!-- label -->
			<foreignObject x="0" y={y - ROW / 2} width={LEFT - 6} height={ROW}>
				<div class="form" class:current={r.isCurrent} title={r.ids ? `composition ${r.ids}` : ''}>
					<span class="glyph hanzi">{r.form}</span>
					<span class="meta">
						{#if r.reading}<i>{r.reading}</i>{/if}
						{#if r.ids}<span class="ids hanzi">{composition(r.ids)}</span>{/if}
					</span>
				</div>
			</foreignObject>
			<!-- lifespan bar -->
			<line x1={x1} x2={Math.max(x2, x1 + 2)} y1={y} y2={y} class="bar" class:current={r.isCurrent} class:replaced={r.replaced && !r.isCurrent} />
			<!-- attestations -->
			{#each r.attestations as a}
				<g class="dot" tabindex="0">
					<circle cx={x(a.year)} cy={y} r="6" class="pt kind-{sources[a.source].kind}" class:inferred={a.inferred} />
					<title>{yearText(a.year)} · {label(a)}</title>
				</g>
			{/each}
			{#if r.isCurrent}
				<circle cx={x(9999)} cy={y} r="6" class="pt now" />
			{/if}
		{/each}
	</svg>
</div>

<ol class="list">
	{#each record.forms as a}
		{@const s = sources[a.source]}
		<li>
			<span class="when">{yearText(a.year)}</span>
			<span class="hanzi big" title={a.ids ? `composition ${a.ids}` : ''}>{a.form}{#if a.ids}<span class="ids"> ({composition(a.ids)})</span>{/if}</span>
			{#if a.reading}<i>{a.reading}</i>{/if}
			<span class="src">{s.zh} <span class="muted">{s.label}, {s.who}</span>{#if a.inferred}<span class="inf"> inferred</span>{/if}</span>
			{#if a.note}<span class="note">{a.note}</span>{/if}
		</li>
	{/each}
</ol>

<style>
	.wrap {
		overflow-x: auto;
	}
	svg {
		display: block;
		font-family: inherit;
	}
	.grid {
		stroke: var(--line);
		stroke-width: 1;
	}
	.tick {
		font-size: 10px;
		fill: var(--muted);
		text-anchor: middle;
	}
	.bar {
		stroke: var(--line);
		stroke-width: 6;
		stroke-linecap: round;
	}
	.bar.replaced {
		stroke: var(--stone);
	}
	.bar.current {
		stroke: var(--accent);
	}
	.link {
		fill: none;
		stroke: var(--accent);
		stroke-width: 1.5;
		stroke-dasharray: 4 3;
	}
	.pt {
		fill: var(--card);
		stroke: var(--fg);
		stroke-width: 1.5;
	}
	.pt.kind-standard {
		fill: var(--fg);
	}
	.pt.kind-proposal,
	.pt.kind-variant {
		stroke-dasharray: 2 2;
	}
	.pt.inferred {
		fill: var(--card);
		stroke-dasharray: 2 2;
	}
	.inf {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
		margin-left: 0.4rem;
	}
	.pt.now {
		fill: var(--accent);
		stroke: var(--accent);
	}
	.dot:focus {
		outline: none;
	}
	.dot:focus .pt,
	.dot:hover .pt {
		r: 8;
	}
	.form {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		height: 100%;
		color: var(--fg);
		font-size: 0.8rem;
		line-height: 1.15;
	}
	.form .glyph {
		font-size: 1.5rem;
		min-width: 1.6em;
	}
	.form.current .glyph {
		color: var(--accent);
		font-weight: 700;
	}
	.meta {
		display: flex;
		flex-direction: column;
		color: var(--muted);
	}
	.ids {
		font-size: 0.7rem;
	}
	.list {
		list-style: none;
		padding: 0;
		margin: 1rem 0 0;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		font-size: 0.9rem;
	}
	.list li {
		display: grid;
		grid-template-columns: 5rem 3rem auto 1fr;
		gap: 0.5rem 0.75rem;
		align-items: baseline;
	}
	.when {
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.big {
		font-size: 1.25rem;
	}
	.note {
		grid-column: 3 / span 2;
		color: var(--muted);
	}
	@media (max-width: 640px) {
		.list li {
			grid-template-columns: 4rem 2.5rem 1fr;
		}
		.note {
			grid-column: 1 / -1;
		}
	}
</style>
