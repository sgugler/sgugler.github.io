<script>
	// Force-directed graph of Gorillaz and their collaborators. d3-force does
	// the layout; Svelte renders the SVG; d3-zoom and d3-drag handle gestures.
	import { onMount } from 'svelte';
	import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force';
	import { select } from 'd3-selection';
	import { zoom, zoomIdentity } from 'd3-zoom';
	import { drag } from 'd3-drag';

	/** @type {{ graph: any, selected?: string|null, onselect?: (id: string|null) => void, kinds?: Set<string>, query?: string }} */
	let { graph, selected = null, onselect = () => {}, kinds = new Set(['feature', 'credit', 'band']), query = '' } = $props();

	let svg;
	let g;
	let width = $state(1200);
	let height = $state(800);
	let nodes = $state([]);
	let links = $state([]);
	let transform = $state(zoomIdentity);
	let sim;

	const GID = 'e21857d5-3256-4547-afb3-4b6ded592596';

	function radius(n) {
		if (n.core) return 26;
		return 5 + Math.sqrt(n.songs.length) * 3.2 + Math.min(n.degree, 12) * 0.35;
	}

	const q = $derived(query.trim().toLowerCase());
	const neighbours = $derived.by(() => {
		if (!selected) return null;
		const s = new Set([selected]);
		for (const l of links) {
			const a = l.source.id ?? l.source;
			const b = l.target.id ?? l.target;
			if (a === selected) s.add(b);
			if (b === selected) s.add(a);
		}
		return s;
	});

	function visible(l) {
		return kinds.has(l.kind);
	}
	function dim(n) {
		if (q) return !n.name.toLowerCase().includes(q);
		if (neighbours) return !neighbours.has(n.id);
		return false;
	}

	onMount(() => {
		const rect = svg.getBoundingClientRect();
		width = rect.width;
		height = Math.max(560, Math.min(900, window.innerHeight - 220));

		nodes = graph.nodes.map((n) => ({ ...n }));
		const byId = new Map(nodes.map((n) => [n.id, n]));
		links = graph.edges.map((e) => ({ ...e, source: byId.get(e.source), target: byId.get(e.target) }));
		const core = byId.get(GID);
		core.fx = width / 2;
		core.fy = height / 2;

		sim = forceSimulation(nodes)
			.force(
				'link',
				forceLink(links)
					.id((d) => d.id)
					.distance((l) => (l.kind === 'feature' ? 140 + 40 * Math.random() : 60))
					.strength((l) => (l.kind === 'feature' ? 0.25 : 0.6))
			)
			.force('charge', forceManyBody().strength((d) => (d.core ? -1200 : -140)))
			.force('center', forceCenter(width / 2, height / 2))
			.force('collide', forceCollide().radius((d) => radius(d) + 6))
			.on('tick', () => {
				nodes = nodes;
			});

		const z = zoom()
			.scaleExtent([0.25, 4])
			.on('zoom', (ev) => (transform = ev.transform));
		select(svg).call(z).on('dblclick.zoom', null);

		const d = drag()
			.on('start', (ev, n) => {
				if (!ev.active) sim.alphaTarget(0.3).restart();
				n.fx = n.x;
				n.fy = n.y;
			})
			.on('drag', (ev, n) => {
				n.fx = ev.x;
				n.fy = ev.y;
			})
			.on('end', (ev, n) => {
				if (!ev.active) sim.alphaTarget(0);
				if (!n.core) {
					n.fx = null;
					n.fy = null;
				}
			});
		// attach drag after first render
		requestAnimationFrame(() => select(g).selectAll('g.node').data(nodes, (n) => n.id).call(d));

		return () => sim.stop();
	});

	$effect(() => {
		// re-bind drag when nodes array identity changes (it does not), kept for safety
		if (g) select(g).selectAll('g.node').data(nodes, (n) => n.id);
	});
</script>

<svg bind:this={svg} {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Collaboration graph">
	<g bind:this={g} transform={transform.toString()}>
		{#each links as l (l.source.id + l.target.id + l.kind)}
			{#if visible(l)}
				<line
					class="link {l.kind}"
					class:dim={dim(l.source) || dim(l.target)}
					class:hot={selected && (l.source.id === selected || l.target.id === selected)}
					x1={l.source.x}
					y1={l.source.y}
					x2={l.target.x}
					y2={l.target.y}
				/>
			{/if}
		{/each}
		{#each nodes as n (n.id)}
			<g
				class="node"
				class:dim={dim(n)}
				class:selected={n.id === selected}
				transform="translate({n.x ?? 0},{n.y ?? 0})"
				onclick={(e) => {
					e.stopPropagation();
					onselect(n.id === selected ? null : n.id);
				}}
				onkeydown={(e) => e.key === 'Enter' && onselect(n.id)}
				role="button"
				tabindex="0"
			>
				<circle r={radius(n)} fill={n.color} />
				{#if n.core || radius(n) > 9 || n.id === selected || (q && !dim(n))}
					<text dy={radius(n) + 12}>{n.name}</text>
				{/if}
				<title>{n.name} · {n.songs.length} Gorillaz track{n.songs.length === 1 ? '' : 's'}</title>
			</g>
		{/each}
	</g>
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		background: var(--card);
		border: 1px solid var(--line);
		border-radius: 0.75rem;
		cursor: grab;
		touch-action: none;
	}
	.link {
		stroke: var(--line);
		stroke-width: 1;
		transition: opacity 0.2s;
	}
	.link.feature {
		stroke: var(--muted);
		stroke-opacity: 0.35;
	}
	.link.credit {
		stroke: var(--accent);
		stroke-opacity: 0.7;
		stroke-width: 1.6;
	}
	.link.band {
		stroke: #ff6fb5;
		stroke-dasharray: 4 3;
		stroke-width: 1.6;
	}
	.link.hot {
		stroke-opacity: 1;
		stroke-width: 2.4;
	}
	.link.dim {
		opacity: 0.08;
	}
	.node {
		cursor: pointer;
		transition: opacity 0.2s;
	}
	.node circle {
		stroke: var(--bg);
		stroke-width: 1.5;
	}
	.node.selected circle {
		stroke: var(--fg);
		stroke-width: 3;
	}
	.node.dim {
		opacity: 0.12;
	}
	text {
		font-size: 11px;
		fill: var(--fg);
		text-anchor: middle;
		pointer-events: none;
		paint-order: stroke;
		stroke: var(--card);
		stroke-width: 3px;
	}
</style>
