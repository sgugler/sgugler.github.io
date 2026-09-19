import { error } from '@sveltejs/kit';
import { elements, bySymbol, homophones } from '$lib/data.js';
import history from '$lib/history.json';

/** One prerendered page per element, e.g. /yanzi/fe/ */
export function entries() {
	return elements.map((e) => ({ symbol: e.symbol.toLowerCase() }));
}

export function load({ params }) {
	const element = bySymbol.get(params.symbol.toLowerCase());
	if (!element) error(404, `No element with symbol "${params.symbol}"`);
	const i = element.z - 1;
	return {
		element,
		prev: elements[i - 1] ?? null,
		next: elements[i + 1] ?? null,
		homophones: homophones(element),
		history: history[element.symbol]
	};
}
