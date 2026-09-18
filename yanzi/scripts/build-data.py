#!/usr/bin/env python3
"""Build src/lib/elements.json from the ChemTexts paper sources.

Usage: python3 scripts/build-data.py /path/to/overleaf_document

Reads table.tex (characters, radicals, phonetics, pinyin, notes), pte.tex
(English names) and the main manuscript (discovery years and codepoints of
the transuranic characters).
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/sgugler/Research/chinese-elements/overleaf_document")
out = Path(__file__).resolve().parent.parent / "src" / "lib" / "elements.json"

ORIGIN = {"SemProp": "property", "SemAncient": "ancient", "SemInt": "transliteration"}
RADICAL_KEY = {"钅": "metal", "金": "metal", "石": "stone", "气": "gas", "氵": "water"}
# Readings where the paper's table differs from the standard dictionary tone.
PINYIN_FIX = {"Be": "pí", "Cm": "jú"}


def delatex(s):
    s = re.sub(r"\\underline\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)
    s = s.replace("$\\rightarrow$", "→").replace("``", "“").replace("''", "”")
    s = s.replace("\\", "")
    return re.sub(r"\s+", " ", s).strip()


def group_period(z):
    """Standard 18-column layout; f-block elements get group None."""
    if z <= 2:
        return (1 if z == 1 else 18, 1)
    for start, period in ((3, 2), (11, 3)):
        if start <= z < start + 8:
            i = z - start
            return (i + 1 if i < 2 else i + 11, period)
    for start, period in ((19, 4), (37, 5)):
        if start <= z < start + 18:
            return (z - start + 1, period)
    for start, period, fstart in ((55, 6, 57), (87, 7, 89)):
        if start <= z < start + 32:
            if z < fstart:
                return (z - start + 1, period)
            if z < fstart + 15:
                return (None, period)
            return (z - fstart - 15 + 4, period)
    raise ValueError(z)


def block(z, group):
    if group is None:
        return "f"
    if group <= 2 or z == 2:
        return "s"
    if group >= 13:
        return "p"
    return "d"


def unicode_block(cp):
    for lo, hi, name in (
        (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
        (0x3400, 0x4DBF, "CJK Extension A"),
        (0x20000, 0x2A6DF, "CJK Extension B"),
        (0x2A700, 0x2B73F, "CJK Extension C"),
        (0x2B740, 0x2B81F, "CJK Extension D"),
        (0x2B820, 0x2CEAF, "CJK Extension E"),
    ):
        if lo <= cp <= hi:
            return name
    return "other"


def plain(pinyin):
    s = unicodedata.normalize("NFD", pinyin)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("ü", "u")


# English names from the periodic table figure.
names = {}
for m in re.finditer(r"\\(?:Natural|Synthetic)Elem\{(\d+)\}\{[^}]*\}\{(\w+)\}\{(\w+)\}", (src / "pte.tex").read_text()):
    names[int(m.group(1))] = m.group(3)
for m in re.finditer(r"\\(?:Natural|Synthetic)Elem\{(\d+)\}\{[^}]*\}\{(\w+)\}\{(\w+)\}", (src / "pte_standard.tex").read_text()):
    names.setdefault(int(m.group(1)), m.group(3))

# Discovery years and codepoints for the transuranic characters.
main = next(src.glob("main_chemtexts*.tex")).read_text()
years, codepoints = {}, {}
for m in re.finditer(r"^(\d+)\s*&\s*(\w+)\s*&\s*(?:\\colorbox\{yellow\}\{)?([\d/–-]+)\}?[^&]*&[^&]*&[^&]*&\s*([0-9A-F]{4,5})", main, re.M):
    z = int(m.group(1))
    years[z] = m.group(3)
    codepoints[z] = int(m.group(4), 16)

rows = []
pat = re.compile(r"\\(SemProp|SemAncient|SemInt)\s*&\s*(\d+)\s*&\s*(\w+)\s*&\s*(\S+)\s*&\s*\\(\w+)\s*&\s*(\S+)\s*&\s*(.+?)\s*&\s*(\S+)\s*&\s*(.*?)\s*(?:\\\\)?\s*$")
for line in (src / "table.tex").read_text().splitlines():
    m = pat.match(line)
    if not m:
        continue
    typ, z, sym, rad, state, phon, char, pinyin, note = m.groups()
    z = int(z)
    img = re.search(r"characters/(\w+)", char)
    cp = codepoints[z] if img else ord(char)
    group, period = group_period(z)
    pinyin = PINYIN_FIX.get(sym, pinyin)
    rows.append({
        "z": z,
        "symbol": sym,
        "name": names[z],
        "char": chr(cp),
        "glyph": img.group(1) if img else None,
        "codepoint": f"U+{cp:04X}",
        "unicodeBlock": unicode_block(cp),
        "pinyin": pinyin,
        "plain": plain(pinyin),
        "radical": rad,
        "radicalKey": RADICAL_KEY[rad],
        "state": state.lower(),
        "phonetic": None if phon == "--" else phon,
        "origin": ORIGIN[typ],
        "note": delatex(note),
        "group": group,
        "period": period,
        "block": block(z, group),
        "discovered": years.get(z),
    })

assert len(rows) == 118, len(rows)
assert all(r["name"] for r in rows)
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {out} ({len(rows)} elements)")
