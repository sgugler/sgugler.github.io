<script>
	import { resolve } from '$app/paths';
</script>

<svelte:head>
	<title>About · 元字</title>
</svelte:head>

<h1>About 元字</h1>

<div class="prose">
	<p>
		元字 <i>yuánzì</i>, “element characters”, is a companion to the paper
		<a href="https://doi.org/10.1007/s40828-026-00222-0">Architecture of Chinese chemical element names</a> by
		Stefan Gugler, Yiyang Cui and Pavlo O. Dral, <i>ChemTexts</i> 12, 11 (2026). The characters, radicals,
		phonetic components, readings and origin notes for all 118 elements come from that paper's tables.
	</p>
	<p>
		The idea and the shape of the site are borrowed from
		<a href="https://adrianhill.de/guzi/">Guzi</a>, Adrian Hill's explorer of Andreas Guder's character
		etymographies: a small, installable app in which every character has a page, search works across scripts and
		readings, and the data is the point.
	</p>

	<h2>What is in the data</h2>
	<ul>
		<li><a href={resolve('/')}>Elements</a>: the 118 current characters, decomposed into radical and phonetic.</li>
		<li><a href={resolve('/phonetic')}>Phonetics</a>: the 117 borrowed components, their own readings and meanings from the Unicode Unihan database, and which syllable of the international name each one echoes.</li>
		<li>History timelines on each element page: every earlier form found in the <a href={resolve('/sources')}>sources</a>, from Hobson's 養氣 of 1849 to the 2017 characters, with links to digitised copies where they exist.</li>
		<li><a href={resolve('/timeline')}>Timeline</a>: the story of the naming system and the people who argued over it.</li>
		<li><a href={resolve('/languages')}>Languages</a>: Japanese, Korean and Vietnamese names from Wikidata next to the Chinese ones, and the Western etymology from Wikipedia's list of element name etymologies.</li>
		<li><a href={resolve('/compounds')}>Compounds</a>: how a binary formula is read today and how it was written in 1871.</li>
	</ul>

	<h2>Sources beyond the paper</h2>
	<ul>
		<li>劉廣定, 中文化學名詞的演變 (上), 科學月刊, October 1985.</li>
		<li>何涓, 益智書會與杜亞泉的中文無機物命名方案, 2010, for the 1901 Educational Association list and Dù Yàquán's 1905 periodic table.</li>
		<li>Chinese Wikipedia, 化学元素的中文命名法 and the individual element articles; Japanese Wikipedia, 元素の中国語名称.</li>
		<li>Hao Chang, Getting to the heart of the matter, 2015; Qiao and Wang, The diachronic evolution of Chinese terms for chemical elements, 2022.</li>
		<li>Unicode Unihan database; Wikidata; Wikipedia, List of chemical element name etymologies.</li>
	</ul>

	<h2>Caveats</h2>
	<p>
		Dates of undated proposals are estimates placed just before the form that replaced them. Two tones differ
		from the paper's table and follow standard dictionaries (鈹 pí, 鋦 jú). Nine characters for elements 104–116
		lie outside the Basic Multilingual Plane and are drawn from outlines; older forms in the same situation show
		their composition instead.
	</p>

	<h2>Code</h2>
	<p>
		A SvelteKit app, prerendered to static files and served next to the Hugo site at sgugler.ch. Source and data
		are in the <a href="https://github.com/sgugler/sgugler.github.io/tree/main/yuanzi">site repository</a>.
	</p>
</div>

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.prose {
		max-width: 68ch;
	}
	.prose h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		margin: 1.5rem 0 0.5rem;
	}
	.prose li {
		margin-bottom: 0.35rem;
	}
</style>
