/// <reference types="@sveltejs/kit" />
import { build, files, prerendered, version } from '$service-worker';

// Everything the app needs is known at build time, so cache it all on install
// and the explorer keeps working offline.
const CACHE = `yanzi-${version}`;
const ASSETS = [...build, ...files, ...prerendered];

self.addEventListener('install', (event) => {
	event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
	);
});

self.addEventListener('fetch', (event) => {
	if (event.request.method !== 'GET') return;
	const url = new URL(event.request.url);
	if (url.origin !== location.origin) return;

	event.respondWith(
		(async () => {
			const cache = await caches.open(CACHE);
			// Build output and static files are immutable per version: cache first.
			if (ASSETS.includes(url.pathname)) {
				const hit = await cache.match(url.pathname);
				if (hit) return hit;
			}
			// Pages: network first, fall back to the prerendered copy.
			try {
				const response = await fetch(event.request);
				if (response.ok) cache.put(event.request, response.clone());
				return response;
			} catch {
				const hit = await cache.match(event.request);
				if (hit) return hit;
				throw new Error('offline and not cached');
			}
		})()
	);
});
