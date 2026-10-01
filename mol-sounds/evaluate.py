#!/usr/bin/env python3
"""Score blind listening results against the automated checks.

Input: one or more JSON files downloaded from sgugler.ch/mol-sounds/ (each
holds, per clip, the listener's presses in seconds and the answer key).

Per listener and clip:
  failing clip  detection delay = first press - automated flag (frames; <0 = earlier)
  stable clip   any press is a false alarm

Writes a table to stdout and results/detection.pdf / .png: detection frame,
human versus automated, for each failing clip.

Usage: python evaluate.py results/*.json [--fps 25] [-o results/detection]
"""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

GG = ["#F8766D", "#00BA38", "#619CFF", "#C77CFF", "#E68613", "#00BFC4"]  # ggplot2 hues
plt.rcParams.update({"font.size": 18, "axes.labelsize": 18, "xtick.labelsize": 16, "ytick.labelsize": 16, "legend.fontsize": 15})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+")
    p.add_argument("--fps", type=float, default=25.0)
    p.add_argument("-o", "--out", default=str(Path(__file__).parent / "results" / "detection"))
    a = p.parse_args()

    rows, false_alarms, stable_total = [], 0, 0
    for n, f in enumerate(a.files):
        d = json.loads(Path(f).read_text())
        who = Path(f).stem
        for c in d["results"]:
            first = c["presses"][0] if c["presses"] else None
            if not c["failing"]:
                stable_total += 1
                false_alarms += first is not None
                continue
            human = None if first is None else c["start"] + first * a.fps
            rows.append({"listener": who, "clip": c["id"], "auto": c["auto_frame"], "human": human, "start": c["start"]})

    print(f"{'listener':20s} clip  auto  human  delay(frames)")
    delays = []
    for r in rows:
        delay = None if r["human"] is None else r["human"] - r["auto"]
        if delay is not None:
            delays.append(delay)
        print(f"{r['listener']:20s} {r['clip']:4s} {r['auto']:5d}  {'miss' if r['human'] is None else int(r['human']):>5}  {'' if delay is None else int(delay)}")
    fa_rate = false_alarms / stable_total if stable_total else float("nan")
    print(f"\nfailing clips detected: {len(delays)}/{len(rows)}; median delay {np.median(delays) if delays else float('nan'):.0f} frames; "
          f"false-alarm rate {false_alarms}/{stable_total} = {fa_rate:.2f}")

    fig, ax = plt.subplots(figsize=(8, 6))
    listeners = sorted({r["listener"] for r in rows})
    for i, who in enumerate(listeners):
        pts = [r for r in rows if r["listener"] == who and r["human"] is not None]
        ax.scatter([r["auto"] for r in pts], [r["human"] for r in pts], s=110, color=GG[i % len(GG)], label=who, zorder=3)
        miss = [r for r in rows if r["listener"] == who and r["human"] is None]
        if miss:
            ax.scatter([r["auto"] for r in miss], [r["start"] + 750 for r in miss], marker="x", s=110, color=GG[i % len(GG)], zorder=3)
    lim = [0, max(1000, max((r["start"] + 750 for r in rows), default=1000))]
    ax.plot(lim, lim, color="0.5", ls="--", lw=1.5, label="automated = human")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("automated detection frame")
    ax.set_ylabel("human detection frame")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out + ".pdf")
    fig.savefig(a.out + ".png", dpi=150)
    print(f"wrote {a.out}.pdf/.png  (points below the diagonal: the listener was earlier; crosses: missed)")


if __name__ == "__main__":
    main()
