<script>
	import { resolve } from '$app/paths';
	import timeline from '$lib/timeline.json';
	import sources from '$lib/sources.json';

	const events = timeline.events;
	const people = timeline.people;
</script>

<svelte:head>
	<title>Timeline · 元字</title>
</svelte:head>

<h1>How the characters were made</h1>
<p class="lead">
	From a Tang alchemist's list of aliases for mercury to the four characters of 2017. The rules that produce every
	element character today were written in Shanghai in 1871 and made law in Nanjing in 1933; almost everything in
	between is missionaries, translators and one journal editor arguing about them.
</p>

<ol class="events">
	{#each events as ev}
		<li>
			<span class="year">{ev.year}</span>
			<div class="body">
				<h2 class="hanzi-title">
					{#if ev.source}<a href={resolve('/sources/[id]', { id: ev.source })}>{ev.title}</a>{:else}{ev.title}{/if}
					{#if ev.source && sources[ev.source].label !== ev.title}<span class="muted sub">{sources[ev.source].label}</span>{/if}
				</h2>
				<p>{ev.text}</p>
				{#if ev.people?.length}
					<p class="who muted">
						{#each ev.people as id, i}{#if i}{' · '}{/if}<span title={people[id].role}>{people[id].name} <span class="hanzi">{people[id].zh}</span></span>{/each}
					</p>
				{/if}
			</div>
		</li>
	{/each}
</ol>

<h2 class="section">The people</h2>
<ul class="people">
	{#each Object.values(people) as p}
		<li class="card">
			<b>{p.name}</b> <span class="hanzi">{p.zh}</span>
			{#if p.dates}<span class="muted">{p.dates}</span>{/if}
			<div class="muted role">{p.role}</div>
		</li>
	{/each}
</ul>

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.lead {
		max-width: 62ch;
		margin: 0 0 1.5rem;
	}
	.events {
		list-style: none;
		padding: 0;
		margin: 0 0 2rem;
		border-left: 2px solid var(--line);
	}
	.events li {
		display: grid;
		grid-template-columns: 5rem 1fr;
		gap: 0.5rem 1rem;
		padding: 0.6rem 0 0.6rem 1rem;
		position: relative;
	}
	.events li::before {
		content: '';
		position: absolute;
		left: -7px;
		top: 1.1rem;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--accent);
	}
	.year {
		font-variant-numeric: tabular-nums;
		font-weight: 600;
	}
	.body h2 {
		font-size: 1.1rem;
		margin: 0 0 0.25rem;
		font-family: var(--font-hanzi);
	}
	.body h2 a {
		color: inherit;
	}
	.sub {
		font-family: system-ui, sans-serif;
		font-weight: 400;
		font-size: 0.9rem;
		margin-left: 0.5rem;
	}
	.body p {
		margin: 0 0 0.25rem;
	}
	.who {
		font-size: 0.85rem;
	}
	.section {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}
	.people {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.6rem;
		grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
	}
	.role {
		font-size: 0.85rem;
	}
	@media (max-width: 560px) {
		.events li {
			grid-template-columns: 1fr;
		}
	}
</style>
