# 元字 yuánzì

A small SvelteKit app that lets you search and explore the Chinese characters of
the 118 chemical elements. It is served at <https://sgugler.ch/yanzi/> next to
the Hugo site: the publish workflow builds it and copies `build/` into
`public/yanzi/`.

The data comes from the element table of

> S. Gugler, Y. Cui, P. O. Dral, *Architecture of Chinese chemical element
> names*, ChemTexts **12**, 11 (2026). <https://doi.org/10.1007/s40828-026-00222-0>

## Develop

```sh
npm install
npm run dev        # http://localhost:5173/yanzi/
npm run build      # static output in build/
```

## Update the data

`src/lib/elements.json` is generated from the paper's LaTeX sources
(`table.tex`, `pte.tex`, the manuscript's Unicode table):

```sh
python3 scripts/build-data.py /path/to/overleaf_document
```

Characters outside the Basic Multilingual Plane (Rf, Db, Sg, Bh, Hs, Ds, Rg,
Fl, Lv) are missing from most fonts, so they are rendered from SVG outlines in
`src/lib/glyphs/`, converted from the paper's PDFs with `pdftocairo -svg`.

## Layout

- `src/routes/+page.svelte` – explorer: search, radical and origin filters,
  periodic table or list view
- `src/routes/[symbol]/` – one prerendered page per element (`/yanzi/fe/`)
- `src/lib/data.js` – search, tone-insensitive pinyin matching, homophones
- `src/service-worker.js`, `static/manifest.webmanifest` – installable, works
  offline
