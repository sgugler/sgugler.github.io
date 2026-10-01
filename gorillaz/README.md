# Gorillaz collaborators

A force-directed graph of every artist credited on a Gorillaz recording and
the links between them (shared recording credits elsewhere, shared bands).
Served at <https://sgugler.ch/gorillaz/>.

## Data

`data/recordings.json` (all Gorillaz recordings with artist credits) and
`data/artists.json` (per collaborator: profile, relations, co-credited
artists) come from the MusicBrainz web service; `scripts/build-graph.py`
turns them into `src/lib/graph.json`. Refetching is a slow, rate-limited job
(about an hour): `scripts/fetch-musicbrainz.py` refreshes `data/artists.json`
after `data/recordings.json` has been fetched.

## Develop

```sh
npm install
npm run dev     # http://localhost:5173/gorillaz/
npm run build
```
