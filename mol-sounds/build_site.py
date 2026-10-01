#!/usr/bin/env python3
"""Precompute everything the /mol-sounds/ page plays and plots.

Writes to ../static/mol-sounds/ (served by Hugo as sgugler.ch/mol-sounds/):
  audio/explore_<traj>_<variant>.mp3   whole trajectories, pitch only / pitch + force loudness
  audio/clip_<id>.mp3                  unlabelled 30 s clips for the blind test
  data/explore.json                    per-frame voice octaves and check series
  data/clips.json                      clip ids, files, durations (no labels)
  data/key.json                        answer key: source, frame range, automated flag

Requires data/*.extxyz from prepare.py and results/ref_stats.json from
`sonify.py ref`.
"""
import json
import random
import subprocess
import tempfile
import warnings
from pathlib import Path

import numpy as np
from ase.io import read

import baseline
import sonify

warnings.filterwarnings("ignore")

HERE = Path(__file__).parent
OUT = HERE.parent / "static" / "mol-sounds"
EV_TO_KCAL = 23.0605

GAIN = 0.5
FPS = 25.0
FORCE_GAIN = 0.35
CLIP_FRAMES = 750  # 30 s at 25 fps
THR = {"energy": 0.5, "force": 5.0, "dist": 0.75}  # eV, eV/Å, Å (as in baseline.py)

# Blind clips. Failing clips start before the automated flag (frame 333) at
# different offsets, plus one late clip where the run has already failed.
CLIPS = [
    ("stable_300K", 0), ("stable_300K", 1100),
    ("long_300K", 2500), ("long_300K", 7000), ("long_300K", 11000), ("long_300K", 15000), ("long_300K", 18500),
    ("fail_400K", 0), ("fail_400K", 120), ("fail_400K", 240), ("fail_400K", 1250),
]
SEED = 7


def mp3(audio, path):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sonify.write_wav(tmp.name, audio)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-ac", "1", "-b:a", "96k", str(path)], check=True)


def checks(path):
    s = baseline.series(read(path, ":"))
    flags = (s["drift"] > THR["energy"]) | (s["fmax"] > THR["force"]) | (s["dmin"] < THR["dist"])
    return s, flags


def main():
    ref = json.loads((HERE / "results" / "ref_stats.json").read_text())
    (OUT / "audio").mkdir(parents=True, exist_ok=True)
    (OUT / "data").mkdir(parents=True, exist_ok=True)

    series = {}
    for name in ("stable_300K", "fail_400K", "long_300K"):
        series[name] = checks(HERE / "data" / f"{name}.extxyz")

    # ---- explore tracks
    explore = {"fps": FPS, "gain": GAIN, "voices": [{"label": g["label"], "f0": g["f0"]} for g in ref["groups"]],
               "thresholds_kcal": {"energy": THR["energy"] * EV_TO_KCAL, "force": THR["force"] * EV_TO_KCAL, "dist": THR["dist"]},
               "trajectories": {}}
    for name in ("stable_300K", "fail_400K"):
        path = HERE / "data" / f"{name}.extxyz"
        for variant, fg in (("pitch", 0.0), ("pitch_force", FORCE_GAIN)):
            audio, info = sonify.render(path, ref, GAIN, FPS, force_gain=fg)
            mp3(audio, OUT / "audio" / f"explore_{name}_{variant}.mp3")
        s, flags = series[name]
        first = baseline.first(flags)
        explore["trajectories"][name] = {
            "frames": len(flags),
            "first_flag": first,
            "octaves": np.round(info["octaves"], 3).T.tolist(),
            "drift_kcal": np.round(s["drift"] * EV_TO_KCAL, 2).tolist(),
            "fmax_kcal": np.round(s["fmax"] * EV_TO_KCAL, 1).tolist(),
            "dmin": np.round(s["dmin"], 3).tolist(),
        }
        print(f"explore {name}: first automated flag {first}")
    (OUT / "data" / "explore.json").write_text(json.dumps(explore))

    # ---- blind clips
    rng = random.Random(SEED)
    order = list(range(len(CLIPS)))
    rng.shuffle(order)
    clips, key = [], {}
    for n, i in enumerate(order):
        src, start = CLIPS[i]
        cid = chr(ord("A") + n)
        stop = start + CLIP_FRAMES
        audio, _ = sonify.render(HERE / "data" / f"{src}.extxyz", ref, GAIN, FPS, start, stop)
        mp3(audio, OUT / "audio" / f"clip_{cid}.mp3")
        _, flags = series[src]
        hit = baseline.first(flags[start:stop])
        clips.append({"id": cid, "file": f"audio/clip_{cid}.mp3", "seconds": CLIP_FRAMES / FPS})
        key[cid] = {"source": src, "start": start, "stop": stop, "failing": src == "fail_400K",
                    "auto_frame": None if hit is None else start + hit,
                    "auto_seconds": None if hit is None else hit / FPS}
        print(f"clip {cid}: {src} {start}-{stop} auto {key[cid]['auto_frame']}")
    (OUT / "data" / "clips.json").write_text(json.dumps({"fps": FPS, "clips": clips}, indent=1))
    (OUT / "data" / "key.json").write_text(json.dumps(key, indent=1))


if __name__ == "__main__":
    main()
