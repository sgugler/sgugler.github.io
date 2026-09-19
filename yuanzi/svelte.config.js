import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
export default {
	kit: {
		adapter: adapter({ pages: 'build', assets: 'build', strict: true }),
		// Served at https://sgugler.ch/yuanzi/ next to the Hugo site.
		paths: { base: '/yuanzi' },
		prerender: { entries: ['*'] }
	}
};
