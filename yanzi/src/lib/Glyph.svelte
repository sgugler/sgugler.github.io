<script>
	// Characters in the CJK Extension planes are missing from most fonts, so
	// those nine are drawn from SVG outlines taken from the paper.
	import rf from './glyphs/rf.svg?raw';
	import db from './glyphs/db.svg?raw';
	import sg from './glyphs/sg.svg?raw';
	import bh from './glyphs/bh.svg?raw';
	import hs from './glyphs/hs.svg?raw';
	import ds from './glyphs/ds.svg?raw';
	import rg from './glyphs/rg.svg?raw';
	import fl from './glyphs/fl.svg?raw';
	import lv from './glyphs/lv.svg?raw';

	const svgs = { rf, db, sg, bh, hs, ds, rg, fl, lv };

	/** @type {{ element: any, size?: string }} */
	let { element, size = '1em' } = $props();
</script>

{#if element.glyph}
	<span class="glyph svg" style:width={size} style:height={size} aria-label={element.char}>
		{@html svgs[element.glyph]}
	</span>
{:else}
	<span class="glyph hanzi" style:font-size={size}>{element.char}</span>
{/if}

<style>
	.glyph {
		display: inline-block;
		line-height: 1;
		vertical-align: middle;
	}
	.svg :global(svg) {
		width: 100%;
		height: 100%;
		display: block;
	}
	.hanzi {
		font-family: var(--font-hanzi);
	}
</style>
