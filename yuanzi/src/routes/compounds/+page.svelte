<script>
	import { resolve } from '$app/paths';
	import { elements, bySymbol } from '$lib/data.js';
	import history from '$lib/history.json';

	let formula = $state('CaCl2');

	const numerals = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
	// Pauling-style electronegativity order for deciding which element is
	// "more electronegative", as IUPAC's formal order does. Rough values suffice.
	const en = {
		F: 3.98, O: 3.44, Cl: 3.16, N: 3.04, Br: 2.96, I: 2.66, S: 2.58, C: 2.55, Se: 2.55, At: 2.2, H: 2.2, P: 2.19,
		As: 2.18, Te: 2.1, B: 2.04, Si: 1.9, Ge: 2.01, Sb: 2.05, Bi: 2.02, Pb: 2.33, Sn: 1.96, Al: 1.61, Zn: 1.65,
		Fe: 1.83, Cu: 1.9, Ag: 1.93, Au: 2.54, Hg: 2.0, Mg: 1.31, Ca: 1.0, Sr: 0.95, Ba: 0.89, Na: 0.93, K: 0.82,
		Li: 0.98, Rb: 0.82, Cs: 0.79, Ti: 1.54, Cr: 1.66, Mn: 1.55, Co: 1.88, Ni: 1.91, Pt: 2.28
	};

	/** Parse "Fe2O3", "CaCl2", "P4S10" into [{symbol, n}]. */
	function parse(f) {
		const out = [];
		const re = /([A-Z][a-z]?)(\d*)/g;
		let m;
		let consumed = 0;
		while ((m = re.exec(f))) {
			if (m.index !== consumed) return null;
			consumed = re.lastIndex;
			if (!bySymbol.has(m[1].toLowerCase())) return null;
			out.push({ symbol: m[1], n: m[2] ? parseInt(m[2], 10) : 1 });
		}
		return consumed === f.length && out.length ? out : null;
	}

	const parts = $derived(parse(formula.trim().replace(/[₀-₉]/g, (c) => String(c.charCodeAt(0) - 8320))));

	function hant(sym) {
		return history[sym].current.hant;
	}
	function hans(sym) {
		return history[sym].current.hans;
	}
	function form1871(sym) {
		const rec = history[sym];
		const a = rec.forms.find((f) => f.source === 'xu1871');
		return a ? a.form : hant(sym);
	}

	const result = $derived.by(() => {
		if (!parts || parts.length !== 2) return null;
		const [a, b] = parts;
		// X is the more electronegative element, E the other.
		const [E, X] = (en[a.symbol] ?? 1.5) >= (en[b.symbol] ?? 1.5) ? [b, a] : [a, b];
		const prefix = (n, drop) => (n === 1 && drop ? '' : numerals[n] ?? String(n));
		const covalent = `${prefix(X.n, false)}${hans(X.symbol)}化${prefix(E.n, true)}${hans(E.symbol)}`;
		const salt = `${hans(X.symbol)}化${hans(E.symbol)}`;
		const old = `${form1871(E.symbol)}${form1871(X.symbol)}${X.n > 1 || E.n > 1 ? ' ' + (E.n > 1 ? numerals[E.n] : '') + (X.n > 1 ? numerals[X.n] : '') : ''}`;
		return { E, X, covalent, salt, old };
	});

	const examples = ['CaCl2', 'CO', 'CO2', 'Fe2O3', 'P4S10', 'NaCl', 'SO3', 'KI', 'H2O'];
</script>

<svelte:head>
	<title>Naming compounds · 元字</title>
</svelte:head>

<h1>Naming a compound</h1>
<p class="lead">
	Binary compounds are named <span class="hanzi">n X 化 m E</span>: the more electronegative element first, 化 “-ide”,
	then the other, with Chinese numerals for the counts. Salts drop the numerals, as in English. In 1871 the
	<span class="hanzi">化學鑑原</span> simply wrote the two element characters side by side, cation first, with small
	numerals for the atoms, which is why every element had to be a single character.
</p>

<div class="input">
	<input type="text" bind:value={formula} placeholder="Formula, e.g. Fe2O3" aria-label="Formula" spellcheck="false" />
	<div class="chips">
		{#each examples as x}<button class="chip" onclick={() => (formula = x)}>{x}</button>{/each}
	</div>
</div>

{#if result}
	<div class="cards">
		<section class="card">
			<h2>Today, covalent style</h2>
			<p class="hanzi big">{result.covalent}</p>
			<p class="muted">Numerical prefixes as in “carbon monoxide”; the prefix of a single E is dropped.</p>
		</section>
		<section class="card">
			<h2>Today, salt style</h2>
			<p class="hanzi big">{result.salt}</p>
			<p class="muted">No prefixes: {result.X.symbol}-ide of {result.E.symbol}. Use 亞 before the metal for the lower oxidation state, 高 for a higher one.</p>
		</section>
		<section class="card">
			<h2>1871, <span class="hanzi">化學鑑原</span></h2>
			<p class="hanzi big">{result.old}</p>
			<p class="muted">Cation first, then the anion character, atom counts as small numerals. Uses the 1871 characters where they differ from today's.</p>
		</section>
	</div>
	<p class="muted small">
		Elements: <a href={resolve('/[symbol]', { symbol: result.E.symbol.toLowerCase() })}>{result.E.symbol}</a> and
		<a href={resolve('/[symbol]', { symbol: result.X.symbol.toLowerCase() })}>{result.X.symbol}</a>. Electronegativity order decides which is X; unusual pairs may come out reversed.
	</p>
{:else if formula.trim()}
	<p class="muted">Enter a binary formula with two known element symbols, such as CaCl2 or P4S10.</p>
{/if}

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.lead {
		max-width: 66ch;
		margin: 0 0 1rem;
	}
	.input {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	input[type='text'] {
		width: 100%;
		max-width: 24rem;
		padding: 0.6rem 1rem;
		font-size: 1.2rem;
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		background: var(--card);
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.cards {
		display: grid;
		gap: 1rem;
		grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
		margin-bottom: 0.75rem;
	}
	h2 {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 0 0 0.5rem;
	}
	.big {
		font-size: 2rem;
		margin: 0 0 0.5rem;
	}
	.small {
		font-size: 0.85rem;
	}
</style>
