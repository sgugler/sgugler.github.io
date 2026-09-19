import elements from './elements.json';
import history from './history.json';

export { elements };

export const bySymbol = new Map(elements.map((e) => [e.symbol.toLowerCase(), e]));

export const radicals = {
	metal: { char: '钅', full: '金', pinyin: 'jīn', meaning: 'metal', state: 'solid metal' },
	stone: { char: '石', full: '石', pinyin: 'shí', meaning: 'stone', state: 'solid non-metal' },
	gas: { char: '气', full: '气', pinyin: 'qì', meaning: 'gas', state: 'gas' },
	water: { char: '氵', full: '水', pinyin: 'shuǐ', meaning: 'water', state: 'liquid' }
};

export const origins = {
	transliteration: {
		label: 'Transliteration',
		description: 'The phonetic half approximates the international name.'
	},
	property: {
		label: 'Meaning-based',
		description: 'The second half also names a property of the element.'
	},
	ancient: {
		label: 'Ancient name',
		description: 'Known in China long before modern chemistry; the old character was kept.'
	}
};

/** Strip tone marks so "qing" matches "qīng"; ü may be typed as u or v. */
export function plain(s) {
	return s
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '')
		.toLowerCase()
		.replace(/ü/g, 'u')
		.replace(/v/g, 'u');
}

const haystacks = new Map(
	elements.map((e) => [
		e.z,
		[e.symbol, e.name, String(e.z), e.char, e.pinyin, e.plain, e.phonetic ?? '', e.radical, e.radicalKey, e.state, e.codepoint, ...(history[e.symbol]?.forms ?? []).flatMap((a) => [a.form, a.reading ?? ''])]
			.map((s) => plain(String(s)))
			.join(' ')
	])
);

/** Elements matching a free-text query plus optional radical / origin filters. */
export function search(query, radical = null, origin = null) {
	const terms = plain(query.trim()).split(/\s+/).filter(Boolean);
	return elements.filter((e) => {
		if (radical && e.radicalKey !== radical) return false;
		if (origin && e.origin !== origin) return false;
		const hay = haystacks.get(e.z);
		return terms.every((t) => hay.includes(t));
	});
}

/** Other elements that share the syllable, split by whether the tone matches too. */
export function homophones(e) {
	const same = [];
	const toneOnly = [];
	for (const other of elements) {
		if (other.z === e.z) continue;
		if (other.pinyin === e.pinyin) same.push(other);
		else if (other.plain === e.plain) toneOnly.push(other);
	}
	return { same, toneOnly };
}
