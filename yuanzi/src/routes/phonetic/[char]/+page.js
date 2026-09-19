import { error } from '@sveltejs/kit';
import phonetics from '$lib/phonetics.json';
import { elements } from '$lib/data.js';

export function entries() {
	return Object.keys(phonetics).map((char) => ({ char }));
}

export function load({ params }) {
	const p = phonetics[params.char];
	if (!p) error(404, `No phonetic component ${params.char}`);
	// Other elements whose reading matches this component's reading, for the
	// "who else sounds like this" list.
	const reading = (p.reading ?? '').split(' ')[0];
	const soundAlikes = elements.filter((e) => e.pinyin === reading && !p.elements.some((x) => x.symbol === e.symbol));
	return { phonetic: p, soundAlikes };
}
