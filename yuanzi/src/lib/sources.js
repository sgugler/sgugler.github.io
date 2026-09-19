import history from './history.json';
import { elements } from './data.js';

/** Which elements each source names, and how many of its forms are still current. */
export function summarise(id) {
	const rows = [];
	for (const e of elements) {
		const rec = history[e.symbol];
		for (const a of rec.forms) {
			if (a.source !== id) continue;
			const cur = rec.current;
			const survives = [cur.hans, cur.hant, cur.tw].includes(a.form);
			rows.push({ element: e, form: a.form, reading: a.reading, note: a.note, ids: a.ids, survives });
		}
	}
	return rows;
}

