<script>
	// Force-directed graph of Gorillaz collaborators. Gorillaz itself is not a
	// node: every artist here is on a Gorillaz track, so the hub would only add
	// 150 spokes. Connected artists pull to the middle; artists with no link to
	// another collaborator settle on an outer ring.
	import { onMount } from 'svelte';
	import { forceSimulation, forceLink, forceManyBody, forceCollide, forceRadial, forceX, forceY } from 'd3-force';
	import { select } from 'd3-selection';
	import { zoom, zoomIdentity } from 'd3-zoom';
	import { drag } from 'd3-drag';

	/** @type {{ graph: any, selected?: string|null, onselect?: (id: string|null) => void, kinds?: Set<string>, query?: string }} */
	let { graph, selected = null, onselect = () => {}, kinds = new Set(['credit', 'band']), query = '' } = $props();

	let svg;
	let width = $state(1200);
	let height = $state(800);
	let nodes = $state([]);
	let links = $state([]);
	let transform = $state(zoomIdentity);
	let sim;

	function radius(n) {
		return 5 + Math.sqrt(n.songs.length) * 3.2;
	}

	const q = $derived(query.trim().toLowerCase());
	const neighbours = $derived.by(() => {
		if (!selected) return null;
		const s = new Set([selected]);
		for (const l of links) {
			if (l.source.id === selected) s.add(l.target.id);
			if (l.target.id === selected) s.add(l.source.id);
		}
		return s;
	});

	function dim(n) {
		if (q) return !n.name.toLowerCase().includes(q);
		if (neighbours) return !neighbours.has(n.id);
		return false;
	}

	onMount(() => {
		const rect = svg.getBoundingClientRect();
		width = rect.width;
		height = Math.max(600, Math.min(950, window.innerHeight - 200));

		// start near the centre so the first frames are not a blob at the origin
		nodes = graph.nodes.map((n, i) => ({
			...n,
			x: width / 2 + Math.cos(i) * 120 * Math.sqrt(i / graph.nodes.length),
			y: height / 2 + Math.sin(i) * 120 * Math.sqrt(i / graph.nodes.length)
		}));
		const byId = new Map(nodes.map((n) => [n.id, n]));
		links = graph.edges
			.filter((e) => e.kind !== 'feature')
			.map((e) => ({ ...e, source: byId.get(e.source), target: byId.get(e.target) }))
			.filter((l) => l.source && l.target);
		const linked = new Set(links.flatMap((l) => [l.source.id, l.target.id]));
		const R = Math.min(width, height) * 0.46;

		sim = forceSimulation(nodes)
			.force('link', forceLink(links).id((d) => d.id).distance(70).strength(0.5))
			.force('charge', forceManyBody().strength(-160))
			.force('collide', forceCollide().radius((d) => radius(d) + 7))
			.force('radial', forceRadial((d) => (linked.has(d.id) ? R * 0.35 : R), width / 2, height / 2).strength((d) => (linked.has(d.id) ? 0.05 : 0.6)))
			.force('x', forceX(width / 2).strength(0.02))
			.force('y', forceY(height / 2).strength(0.02))
			.on('tick', () => {
				nodes = nodes;
			});
		// settle the layout before the first paint
		sim.stop();
		for (let i = 0; i < 200; i++) sim.tick();
		nodes = nodes;
		sim.alpha(0.3).restart();

		const z = zoom()
			.scaleExtent([0.3, 4])
			.on('zoom', (ev) => (transform = ev.transform));
		select(svg).call(z).on('dblclick.zoom', null);
		// fit the settled layout into the viewport
		const xs = nodes.map((n) => n.x);
		const ys = nodes.map((n) => n.y);
		const [x0, x1, y0, y1] = [Math.min(...xs) - 40, Math.max(...xs) + 40, Math.min(...ys) - 30, Math.max(...ys) + 30];
		const k = Math.min(width / (x1 - x0), height / (y1 - y0), 1.5);
		select(svg).call(z.transform, zoomIdentity.translate(width / 2 - (k * (x0 + x1)) / 2, height / 2 - (k * (y0 + y1)) / 2).scale(k));

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
				n.fx = null;
				n.fy = null;
			});
		requestAnimationFrame(() => select(svg).selectAll('g.node').data(nodes, (n) => n.id).call(d));

		return () => sim.stop();
	});
</script>

<svg bind:this={svg} {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Collaboration graph">
	<g transform={transform.toString()}>
		{#each links as l (l.source.id + l.target.id + l.kind)}
			{#if kinds.has(l.kind)}
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
				<text dy={radius(n) + 11}>{n.name}</text>
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
		stroke-width: 1.4;
		transition: opacity 0.2s;
	}
	.link.credit {
		stroke: var(--accent);
		stroke-opacity: 0.7;
	}
	.link.band {
		stroke: #ff6fb5;
		stroke-dasharray: 4 3;
	}
	.link.hot {
		stroke-opacity: 1;
		stroke-width: 2.6;
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
		font-size: 10px;
		fill: var(--fg);
		text-anchor: middle;
		pointer-events: none;
		paint-order: stroke;
		stroke: var(--card);
		stroke-width: 3px;
	}
</style>
