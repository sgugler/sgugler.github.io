#!/usr/bin/env python3
"""Build src/lib/graph.json from MusicBrainz data in data/.

data/recordings.json  every Gorillaz recording with artist credits
data/artists.json     one entry per collaborator: profile, artist relations,
                      and the artists they share recording credits with

Nodes: Gorillaz and everyone credited on a Gorillaz recording.
Edges: "feature"  collaborator credited on a Gorillaz recording (with songs)
       "credit"   two collaborators credited together on some other recording
       "band"     member-of-band / collaboration relations between collaborators
"""
import json
import re
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = root / "data"
GID = "e21857d5-3256-4547-afb3-4b6ded592596"

recordings = json.loads((data / "recordings.json").read_text())
artists = json.loads((data / "artists.json").read_text())
releases = json.loads((data / "releases.json").read_text())

# Only recordings that appear on an official Gorillaz release count. This
# drops bootleg mashups and mislabelled uploads that MusicBrainz also credits
# to Gorillaz. Each recording maps to its best release group: album first,
# then EP/single, then compilations.
RANK = {"Album": 0, "EP": 1, "Single": 2, "Other": 3, "Broadcast": 4}
EXCLUDE_RELEASE_GROUPS = {"East Type Beat"}  # credited to Gorillaz in MusicBrainz, not a Gorillaz release
albums = {}
for rel in releases:
    if rel.get("status") != "Official":
        continue
    rg = rel.get("release-group") or {}
    title = rg.get("title") or rel["title"]
    if title in EXCLUDE_RELEASE_GROUPS:
        continue
    rank = RANK.get(rg.get("primary-type"), 3) + (5 if rg.get("secondary-types") else 0)
    date = rel.get("date") or rg.get("first-release-date") or ""
    for m in rel.get("media", []):
        for t in m.get("tracks", []):
            rid = t["recording"]["id"]
            cand = (rank, date, title)
            if rid not in albums or cand < albums[rid]:
                albums[rid] = cand
UNKNOWN_ARTIST = "125ec42a-7229-4250-afc5-e057484327fe"
# Cover projects credited to Gorillaz in MusicBrainz but not Gorillaz recordings.
EXCLUDE_ARTISTS = {"Rhythms del Mundo", "Red Village"}

ERAS = [
    (2000, 2003, "Gorillaz", "#7ed957"),
    (2004, 2007, "Demon Days", "#e94f37"),
    (2008, 2012, "Plastic Beach / The Fall", "#3fa7d6"),
    (2013, 2016, "Interim", "#9b9b9b"),
    (2017, 2017, "Humanz", "#f2c14e"),
    (2018, 2019, "The Now Now", "#c77dff"),
    (2020, 2021, "Song Machine", "#ff6fb5"),
    (2022, 2024, "Cracker Island", "#ff9f1c"),
    (2025, 2100, "The Mountain", "#5ee6c8"),
]


def era(year):
    for lo, hi, name, color in ERAS:
        if year and lo <= year <= hi:
            return name, color
    return "Unknown", "#777777"


def clean_title(t):
    return re.sub(r"\s*\((live|demo|instrumental|remix|refix|edit|radio edit|acoustic|mix|version|album version|single version|clean|explicit|episode)[^)]*\)\s*$", "", t, flags=re.I).strip()


# feature edges
songs = defaultdict(dict)  # artist -> title -> year
names = {}
# A featured recording is often a separate MusicBrainz entry from the album
# track, so also accept recordings whose cleaned title matches an official track.
official_titles = {}
for rel in releases:
    if rel.get("status") != "Official":
        continue
    rg = rel.get("release-group") or {}
    title = rg.get("title") or rel["title"]
    if title in EXCLUDE_RELEASE_GROUPS:
        continue
    rank = RANK.get(rg.get("primary-type"), 3) + (5 if rg.get("secondary-types") else 0)
    date = rel.get("date") or rg.get("first-release-date") or ""
    for m in rel.get("media", []):
        for t in m.get("tracks", []):
            key = clean_title(t["title"]).lower()
            cand = (rank, date, title)
            if key not in official_titles or cand < official_titles[key]:
                official_titles[key] = cand

# Official Gorillaz tracks that were released on someone else's record.
EXTRA_TITLES = {"gorillaz on my mind": (3, "2003", "Laugh Now, Cry Later soundtrack")}
official_titles.update(EXTRA_TITLES)

for r in recordings:
    title = clean_title(r["title"])
    hit = albums.get(r["id"]) or official_titles.get(title.lower())
    if not hit:
        continue
    year = int(r["first-release-date"][:4]) if r.get("first-release-date") else None
    if title.lower() in ("[untitled]", "[silence]"):
        continue
    album = hit[2]
    for ac in r["artist-credit"]:
        if not isinstance(ac, dict):
            continue
        aid = ac["artist"]["id"]
        if aid == GID or aid == UNKNOWN_ARTIST or ac["artist"]["name"] in EXCLUDE_ARTISTS:
            continue
        names[aid] = ac["artist"]["name"]
        prev = songs[aid].get(title)
        if prev is None or (year and prev[0] and year < prev[0]):
            songs[aid][title] = (year, album)

nodes = {GID: {"id": GID, "name": "Gorillaz", "type": "Group", "core": True, "songs": [], "era": "Gorillaz", "color": "#ffffff", "degree": 0}}
for aid, name in names.items():
    a = artists.get(aid, {})
    s = sorted(songs[aid].items(), key=lambda kv: (kv[1][0] or 9999, kv[0]))
    first = next((y for _, (y, _a) in s if y), None)
    ename, color = era(first)
    nodes[aid] = {
        "id": aid,
        "name": a.get("name", name),
        "type": a.get("type"),
        "country": a.get("country"),
        "area": a.get("area"),
        "begin": a.get("begin"),
        "disambiguation": a.get("disambiguation"),
        "tags": a.get("tags", []),
        "wikipedia": a.get("wikipedia"),
        "wikidata": a.get("wikidata"),
        "songs": [{"title": t, "year": y, "album": a} for t, (y, a) in s],
        "first": first,
        "era": ename,
        "color": color,
        "degree": 0,
    }

edges = []
for aid in names:
    edges.append({"source": GID, "target": aid, "kind": "feature", "n": len(nodes[aid]["songs"])})

# collaborator-collaborator edges
seen = set()
for aid, a in artists.items():
    if aid not in nodes:
        continue
    for bid, co in a.get("co", {}).items():
        if bid in nodes and bid != aid and bid != GID:
            key = tuple(sorted((aid, bid)))
            if key in seen:
                continue
            seen.add(key)
            titles = [clean_title(t) for t in co["titles"]]
            # drop Gorillaz songs themselves: those are the feature edges
            gz = {s["title"].lower() for s in nodes[aid]["songs"]} | {s["title"].lower() for s in nodes[bid]["songs"]}
            titles = [t for t in dict.fromkeys(titles) if t.lower() not in gz]
            if titles:
                edges.append({"source": key[0], "target": key[1], "kind": "credit", "titles": titles[:6]})
    for rel in a.get("rels", []):
        bid = rel["id"]
        if bid in nodes and bid != GID and rel["type"] in ("member of band", "collaboration", "supporting musician", "founder", "subgroup", "is person", "vocal supporting musician", "instrumental supporting musician"):
            key = tuple(sorted((aid, bid, rel["type"])))
            if key in seen:
                continue
            seen.add(key)
            edges.append({"source": aid, "target": bid, "kind": "band", "rel": rel["type"]})

for e in edges:
    nodes[e["source"]]["degree"] += 1
    nodes[e["target"]]["degree"] += 1

out = {"nodes": [n for n in nodes.values() if not n.get("core")], "edges": [e for e in edges if e["kind"] != "feature"], "eras": [{"name": n, "color": c, "from": lo, "to": hi} for lo, hi, n, c in ERAS]}
(root / "src/lib/graph.json").write_text(json.dumps(out, ensure_ascii=False) + "\n")
kinds = defaultdict(int)
for e in edges:
    kinds[e["kind"]] += 1
print(f"{len(nodes)} nodes, {len(edges)} edges {dict(kinds)}; {sum(1 for a in names if a in artists)} of {len(names)} collaborators fetched")
