import sources from '$lib/sources.json';
import { summarise } from '$lib/sources.js';

export function load() {
	const list = Object.entries(sources)
		.map(([id, s]) => {
			const rows = summarise(id);
			return { id, ...s, count: rows.length, survivors: rows.filter((r) => r.survives).length };
		})
		.sort((a, b) => (a.year ?? (a.kind === 'tradition' ? -1 : 9999)) - (b.year ?? (b.kind === 'tradition' ? -1 : 9999)));
	return { list };
}
