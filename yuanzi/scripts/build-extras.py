#!/usr/bin/env python3
"""Build the phonetic-component, cross-language and etymology data.

Inputs in data/: unihan.json (readings and glosses from the Unicode Unihan
database), languages.json (Wikidata labels), etymology.txt (the wikitext of
Wikipedia's "List of chemical element name etymologies"), overrides in this
file for the syllable each phonetic component transliterates.

Outputs in src/lib/: phonetics.json, extras.json (per element: source name,
syllables, matched syllable, etymology, ja/ko/vi names).
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = root / "data"
lib = root / "src/lib"
elements = json.loads((lib / "elements.json").read_text())
unihan = json.loads((data / "unihan.json").read_text())
languages = {l["symbol"]: l for l in json.loads((data / "languages.json").read_text())}

# International name whose sound the phonetic approximates, where it is not
# the English name.
SOURCE_NAME = {
    "Na": "natrium", "K": "kalium", "W": "wolframium", "Sb": "stibium",
    "Ru": "ruthenium", "Rh": "rhodium", "Sn": "stannum",
}

# Hand-checked syllable index (0-based) where the heuristic below is wrong or
# ambiguous, plus a short display of the matched part.
OVERRIDE = {
    "Al": 1, "As": 1, "Rn": 1, "I": 1, "Sc": 0, "Ar": 0, "Sb": 0, "Te": 0,
    "Ta": 0, "Tl": 0, "Th": 0, "Ti": 0, "Tm": 0, "Tb": 0, "Tc": 0, "Kr": 0,
    "Ge": 0, "Cs": 0, "Cf": 0, "Gd": 0, "Ga": 0, "Ho": 0, "Hf": 0, "He": 0,
    "Cd": 0, "Ir": 0, "Er": 0, "Eu": 0, "Es": 0, "Os": 0, "Ac": 0, "Am": 0,
    "In": 0, "Y": 0, "Yb": 0, "U": 0, "Og": 0, "Nh": 0, "Ni": 0, "Nb": 0,
    "Ne": 0, "Nd": 0, "No": 0, "Np": 0, "Md": 0, "Mo": 0, "Mn": 0, "Mg": 0,
    "Mt": 0, "Mc": 0, "Lr": 0, "Lu": 0, "Li": 0, "La": 0, "Lv": 0, "Se": 0,
    "Sr": 0, "Sm": 0, "Sg": 0, "Si": 0, "Rb": 0, "Re": 0, "Ra": 0, "Rf": 0,
    "Rg": 0, "Ru": 0, "Rh": 0, "Pd": 0, "Pa": 0, "Pu": 0, "Pm": 0, "Po": 0,
    "Pr": 0, "Bk": 0, "Bi": 0, "Ba": 0, "Bh": 0, "Be": 0, "Db": 0, "Dy": 0,
    "Ds": 0, "Fr": 0, "Fm": 0, "Fl": 0, "F": 0, "Zr": 0, "Zn": 0, "V": 0,
    "Na": 0, "K": 0, "W": 0, "Cr": 0, "Co": 0, "Ca": 0, "Ce": 0, "Cm": 0,
    "Cn": 0, "At": 0, "Xe": 0, "Ts": 0, "Hs": 0, "Ta_": 0,
}

# Elements whose second half is meaning-based or whose name is ancient are
# not transliterations; they get no syllable.
NOT_TRANSLITERATED = {e["symbol"] for e in elements if e["origin"] != "transliteration"}


def syllables(name):
    """Crude split of a Latin/English element name into pronounceable chunks."""
    name = name.lower()
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy]+(?![aeiouy]))?", name)
    if not parts:
        return [name]
    # glue leftover consonants at the end (e.g. "ium" endings are fine)
    joined = "".join(parts)
    if len(joined) < len(name):
        parts[-1] += name[len(joined):]
    return parts


extras = {}
phonetics = {}
for e in elements:
    sym = e["symbol"]
    src = SOURCE_NAME.get(sym, e["name"].lower())
    syl = syllables(src)
    idx = None
    if sym not in NOT_TRANSLITERATED and e["phonetic"]:
        idx = OVERRIDE.get(sym, 0)
        idx = min(idx, len(syl) - 1)
    lang = languages.get(sym, {})
    extras[sym] = {
        "sourceName": src,
        "syllables": syl,
        "matched": idx,
        "ja": lang.get("ja"),
        "ko": lang.get("ko"),
        "vi": lang.get("vi"),
    }
    ph = e["phonetic"]
    if ph:
        u = unihan.get(ph, {})
        p = phonetics.setdefault(ph, {
            "char": ph,
            "reading": u.get("kMandarin"),
            "definition": u.get("kDefinition"),
            "cantonese": u.get("kCantonese"),
            "elements": [],
        })
        p["elements"].append({"symbol": sym, "z": e["z"], "name": e["name"], "char": e["char"], "glyph": e["glyph"], "pinyin": e["pinyin"], "matched": idx, "syllables": syl})

# Etymology from Wikipedia's list (template rows).
etym_path = data / "etymology.txt"
if etym_path.exists():
    txt = etym_path.read_text()

    def clean(s):
        s = re.sub(r"<ref[^>]*/>", "", s)
        s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
        s = re.sub(r"\{\{lang\|[^|}]+\|([^}]*)\}\}", r"\1", s)
        s = re.sub(r"\{\{translit\|[^|}]+\|([^}]*)\}\}", r"\1", s)
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
        s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s)
        s = re.sub(r"'{2,}", "", s)
        s = re.sub(r"<br\s*/?>", "; ", s)
        s = re.sub(r"<[^>]+>", "", s)
        return re.sub(r"\s+", " ", s).strip(" ;")

    for m in re.finditer(r"\{\{List of chemical element name etymologies row\s*(.*?)\n\}\}", txt, re.S):
        body = m.group(1)
        fields = {}
        for f in re.split(r"\n\s*\|", "\n" + body):
            if "=" in f:
                k, v = f.split("=", 1)
                fields[k.strip()] = v.strip()
        sym = fields.get("symbol", "").strip()
        if sym in extras:
            extras[sym]["etymology"] = {
                "language": clean(fields.get("word-origin-lang", "")),
                "word": clean(fields.get("word-origin", "")),
                "meaning": clean(fields.get("meaning", "")).strip('"'),
                "kind": clean(fields.get("origin", "")),
            }

(lib / "extras.json").write_text(json.dumps(extras, ensure_ascii=False, indent=1) + "\n")
(lib / "phonetics.json").write_text(json.dumps(phonetics, ensure_ascii=False, indent=1) + "\n")
missing = [s for s, x in extras.items() if "etymology" not in x]
print(f"{len(phonetics)} phonetic components; etymology missing for {missing}")
for sym, x in extras.items():
    if x["matched"] is not None:
        print(sym, x["syllables"], "->", x["syllables"][x["matched"]], "|", next(e for e in elements if e["symbol"] == sym)["pinyin"])
