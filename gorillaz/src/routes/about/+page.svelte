<script>
	import { graph } from '$lib/data.js';
	const n = graph.nodes.length - 1;
	const feat = graph.edges.filter((e) => e.kind === 'feature').length;
	const credit = graph.edges.filter((e) => e.kind === 'credit').length;
	const band = graph.edges.filter((e) => e.kind === 'band').length;
</script>

<svelte:head><title>About – Gorillaz collaborators</title></svelte:head>

<h1>About</h1>
<div class="prose">
	<p>
		Gorillaz is a band built out of guests. This graph shows every artist credited on a Gorillaz recording in
		<a href="https://musicbrainz.org/">MusicBrainz</a>, and the links between those guests that have nothing to do
		with Gorillaz: tracks they recorded together elsewhere, and bands they share.
	</p>
	<h2>How it is built</h2>
	<ul>
		<li>All recordings credited to Gorillaz are fetched from MusicBrainz; every other artist in a credit becomes a node ({n} artists, {feat} feature links).</li>
		<li>For each of those artists, up to 1000 of their own recordings are scanned for credits shared with another Gorillaz collaborator ({credit} links, Gorillaz tracks excluded).</li>
		<li>MusicBrainz artist relations add band memberships and named collaborations between collaborators ({band} links).</li>
		<li>Colour is the era of the artist's first Gorillaz track, by first release date; size is the number of tracks.</li>
	</ul>
	<h2>Caveats</h2>
	<p>
		MusicBrainz credits are only as complete as its editors made them. Remixes, live versions and alternate mixes are
		folded into one title where the name allows. Artists with thousands of recordings are scanned only partially, so
		a shared credit can be missed. Writers and producers who are not in the artist credit are not included.
	</p>
	<h2>Code</h2>
	<p>A SvelteKit app with d3-force, prerendered and served next to the rest of sgugler.ch. Source and the build script are in the <a href="https://github.com/sgugler/sgugler.github.io/tree/main/gorillaz">site repository</a>.</p>
</div>

<style>
	.prose {
		max-width: 66ch;
	}
	h2 {
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 1.4rem 0 0.4rem;
	}
</style>
