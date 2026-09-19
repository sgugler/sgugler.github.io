#!/usr/bin/env python3
"""Merge the historical-name sources in data/ into src/lib/history.json.

Inputs (all in data/):
  sources.json      the works and standards that attest a form
  early-table.json  the 1868–1871 comparison table (金石識別, 格物入門, 化學初階, 化學鑑原)
  curated-1/2.json  attestations collected from the ChemTexts paper, Liu Guangding
                    (科學月刊 1985), He Juan (2010) and the element articles
  variants.json     simplified / traditional / Taiwan forms and readings

Output: one record per element symbol with a chronologically ordered list of
attested forms, ready for the timeline on the element page.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = root / "data"
elements = json.loads((root / "src/lib/elements.json").read_text())
sources = json.loads((data / "sources.json").read_text())
early = json.loads((data / "early-table.json").read_text())
variants = {v["symbol"]: v for v in json.loads((data / "variants.json").read_text())}
curated = json.loads((data / "curated-1.json").read_text()) + json.loads((data / "curated-2.json").read_text())

# Characters in the early table that most fonts lack, with their composition.
IDS = {"𥑢": "⿰石布", "𨦗": "⿰金卜", "𳆗": "⿱信金"}

attest = {e["symbol"]: [] for e in elements}

# The comparison table mixes simplified and traditional spellings; write each
# current character in its traditional form so one form gets one row.
to_hant = {v["hans"]: v["hant"] for v in variants.values() if v.get("hant") and v["hans"] != v["hant"]}

for row in early:
    for src in ("martin1868", "kerr1870", "macgowan1871", "xu1871"):
        form = row.get(src)
        if form:
            form = to_hant.get(form, form)
            entry = {"form": form, "source": src}
            if form in IDS:
                entry["ids"] = IDS[form]
            attest[row["symbol"]].append(entry)

for c in curated:
    sym = c.pop("symbol")
    assert sym in attest, sym
    assert c["source"] in sources, c["source"]
    attest[sym].append(c)


def year_of(entry, entries):
    """Sort key. Undated kinds are placed relative to what they precede."""
    y = entry.get("year") or sources[entry["source"]]["year"]
    if y is not None:
        return y
    kind = entry["source"]
    if kind == "ancient":
        return 0
    if kind == "tw":
        return 9999
    # proposal / bloc / japanese: just before the form that replaced it
    for other in entries:
        if other.get("succeeds") == entry["form"]:
            oy = sources[other["source"]]["year"]
            if oy:
                return oy - 1
    return 1900


# Standards that fixed a name without a per-element citation available:
# the 1933 Principles covered every element known then, and the paper records
# only three later changes; the 1991 Chemical Terms finalised all elements to
# 109. Where no dated attestation of the current form exists, add one from
# the relevant standard and flag it as inferred.
NAMED_LATER = {"Tc": "prc1991", "Pm": "prc1991", "At": "prc1991", "Fr": "prc1991"}
INFERRED_NOTE = {
    "moe1933": "Inferred: known by 1933, when the Principles fixed one character per element, and no later change is recorded.",
    "prc1991": "Inferred: finalised at the latest in Chemical Terms (1991), which settled every element up to 109.",
}
for e in elements:
    sym = e["symbol"]
    v = variants.get(sym, {})
    hant = v.get("hant") or e["char"]
    dated = any(a["form"] == hant and sources[a["source"]]["year"] for a in attest[sym])
    if dated or e["z"] > 109:
        continue
    if sym in NAMED_LATER:
        src, inferred = NAMED_LATER[sym], sym not in ("Tc", "Pm", "At", "Fr")
    elif e["z"] <= 92:
        src, inferred = "moe1933", True
    else:
        src, inferred = "prc1991", True
    entry = {"form": hant, "source": src, "reading": e["pinyin"]}
    if inferred:
        entry["inferred"] = True
        entry["note"] = INFERRED_NOTE[src]
    else:
        entry["note"] = "Named in Chemical Terms (1991), which gave technetium, promethium, astatine and francium their final characters."
    attest[sym].append(entry)

out = {}
for e in elements:
    sym = e["symbol"]
    entries = attest[sym]
    for en in entries:
        en["year"] = year_of(en, entries)
    entries.sort(key=lambda en: (en["year"], en["form"]))
    # drop exact duplicates (same form, same source)
    seen, uniq = set(), []
    for en in entries:
        key = (en["form"], en["source"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(en)
    v = variants.get(sym, {})
    out[sym] = {
        "forms": uniq,
        "current": {
            "hans": e["char"],
            "hant": v.get("hant") or e["char"],
            "pinyin": e["pinyin"],
            "tw": v.get("tw") or v.get("hant") or e["char"],
            "twPinyin": v.get("tw_pinyin") or e["pinyin"],
        },
    }

with_history = sum(1 for s in out.values() if s["forms"])
(root / "src/lib/history.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
(root / "src/lib/sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=1) + "\n")
(root / "src/lib/timeline.json").write_text((data / "timeline.json").read_text())
print(f"{with_history} elements with attested earlier forms; {sum(len(s['forms']) for s in out.values())} attestations")
