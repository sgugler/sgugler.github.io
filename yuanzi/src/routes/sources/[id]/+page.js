import { error } from '@sveltejs/kit';
import sources from '$lib/sources.json';
import { summarise } from '$lib/sources.js';

export function entries() {
	return Object.keys(sources).map((id) => ({ id }));
}

export function load({ params }) {
	const s = sources[params.id];
	if (!s) error(404, `No source ${params.id}`);
	return { id: params.id, source: s, rows: summarise(params.id) };
}
