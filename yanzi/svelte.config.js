import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
export default {
	kit: {
		adapter: adapter({ pages: 'build', assets: 'build', strict: true }),
		// Served at https://sgugler.ch/yanzi/ next to the Hugo site.
		paths: { base: '/yanzi' },
		prerender: { entries: ['*'] }
	}
};
