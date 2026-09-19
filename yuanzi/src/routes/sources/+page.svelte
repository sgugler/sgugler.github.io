<script>
	import { resolve } from '$app/paths';
	let { data } = $props();
</script>

<svelte:head>
	<title>Sources · 元字</title>
</svelte:head>

<h1>Sources</h1>
<p class="lead">
	Every book, journal and standard that attests a form in the history timelines. The bar shows how many of the
	forms a source used are still the current character somewhere: the Xú–Fryer characters of 1871 are the durable
	core, Martin's 1868 glosses almost all died.
</p>

<ul class="list">
	{#each data.list as s}
		<li class="card">
			<a class="title" href={resolve('/sources/[id]', { id: s.id })}>
				<span class="hanzi zh">{s.zh}</span>
				<span class="label">{s.label}{#if s.year}<span class="muted"> · {s.year}</span>{/if}</span>
			</a>
			<div class="muted who">{s.who}</div>
			{#if s.count}
				<div class="bar" title="{s.survivors} of {s.count} forms still current">
					<span style:width="{(100 * s.survivors) / s.count}%"></span>
					<small>{s.survivors} / {s.count} forms survive</small>
				</div>
			{/if}
		</li>
	{/each}
</ul>

<style>
	h1 {
		margin: 0 0 0.5rem;
	}
	.lead {
		max-width: 62ch;
		margin: 0 0 1.25rem;
	}
	.list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.6rem;
		grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
	}
	.title {
		display: flex;
		flex-direction: column;
		text-decoration: none;
	}
	.zh {
		font-size: 1.3rem;
	}
	.who {
		font-size: 0.85rem;
		margin: 0.2rem 0 0.5rem;
	}
	.bar {
		position: relative;
		height: 1.3rem;
		background: var(--line);
		border-radius: 0.4rem;
		overflow: hidden;
	}
	.bar span {
		position: absolute;
		inset: 0 auto 0 0;
		background: var(--accent);
		opacity: 0.55;
	}
	.bar small {
		position: relative;
		padding-left: 0.5rem;
		line-height: 1.3rem;
	}
</style>
