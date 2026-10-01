import graph from './graph.json';

export const GID = 'e21857d5-3256-4547-afb3-4b6ded592596';
export { graph };
export const byId = new Map(graph.nodes.map((n) => [n.id, n]));
export const artists = graph.nodes.filter((n) => !n.core).sort((a, b) => b.songs.length - a.songs.length || a.name.localeCompare(b.name));

/** Edges touching an artist, with the other end resolved. */
export function connections(id) {
	return graph.edges
		.filter((e) => e.source === id || e.target === id)
		.map((e) => ({ ...e, other: byId.get(e.source === id ? e.target : e.source) }))
		.filter((e) => e.other);
}
