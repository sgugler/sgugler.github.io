import { error } from '@sveltejs/kit';
import { artists, byId, connections, GID } from '$lib/data.js';

export function entries() {
	return artists.map((a) => ({ id: a.id }));
}

export function load({ params }) {
	const artist = byId.get(params.id);
	if (!artist || artist.id === GID) error(404, 'No such artist');
	return { artist, connections: connections(artist.id).filter((c) => c.other.id !== GID) };
}
