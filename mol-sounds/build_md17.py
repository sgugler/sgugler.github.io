#!/usr/bin/env python3
"""Sonify MD17 molecules on one shared instrument.

MD17 (Chmiela et al. 2017): DFT (PBE+vdW-TS) ab initio MD at 500 K, 0.5 fs
steps, frames in time order. For each molecule:
  - bonds from the first frame of the explore segment
  - voices by element pair with fixed notes (sonify.BASE_BY_PAIR)
  - the spread σ and mean of each voice feature are pooled over all
    molecules, so stiffer or floppier molecules keep their character
  - one 60 s explore track with animation data, and two 15 s quiz clips from
    other parts of the trajectory

Writes ../static/mol-sounds/audio/md17_*.mp3, data/traj/md17_*.json,
data/md17_quiz.json. Input: data/md17/md17_<name>.npz.
"""
import json
import random
from pathlib import Path

import numpy as np
from ase import Atoms

import sonify
import trajdata
from build_site import mp3

HERE = Path(__file__).parent
OUT = HERE.parent / "static" / "mol-sounds"
FPS, GAIN = 25.0, 0.5
EXPLORE = (50_000, 51_500)  # 60 s
QUIZ_AT = (0.55, 0.9)  # quiz clips at these fractions of each trajectory
QUIZ_LEN = 375  # 15 s
STATS_FRAMES = slice(0, 200_000, 20)  # 10 000 frames per molecule for the pooled statistics

MOLS = [("ethanol", "ethanol"), ("malonaldehyde", "malonaldehyde"), ("benzene2017", "benzene"),
        ("toluene", "toluene"), ("naphthalene", "naphthalene"), ("salicylic", "salicylic acid"),
        ("aspirin", "aspirin"), ("uracil", "uracil")]


def frames(z, R):
    return [Atoms(z, positions=r) for r in R]


def main():
    (OUT / "data" / "traj").mkdir(parents=True, exist_ok=True)
    loaded = {}
    for key, name in MOLS:
        d = np.load(HERE / "data" / "md17" / f"md17_{key}.npz")
        loaded[key] = (d["z"], d["R"])
        print(f"loaded {name}: {d['R'].shape[0]} frames")

    # bonds, groups and per-bond means per molecule; feature values pooled per element pair
    refs, pooled = {}, {}
    for key, name in MOLS:
        z, R = loaded[key]
        first = Atoms(z, positions=R[EXPLORE[0]])
        bonds = sonify.detect_bonds(first)
        groups = sonify.groups_for(first, bonds, k=6)
        sample = frames(z, R[STATS_FRAMES])
        L = sonify.bond_lengths(sample, bonds)
        bond_eq = L.mean(axis=0)
        X = sonify.voice_features(L, bond_eq, groups)
        for n, g in enumerate(groups):
            pooled.setdefault(g["label"], []).append(X[:, n])
        refs[key] = {"bonds": bonds, "bond_eq": bond_eq.tolist(), "groups": groups}
    stats = {lab: (float(np.concatenate(v).mean()), float(np.concatenate(v).std())) for lab, v in pooled.items()}
    for lab, (m, s) in stats.items():
        print(f"pooled {lab}: mean {m:.4f} Å std {s:.4f} Å over {len(pooled[lab])} molecules")

    index, quiz = [], []
    for key, name in MOLS:
        z, R = loaded[key]
        ref = refs[key]
        ref["groups"] = [{**g, "mean": stats[g["label"]][0], "std": stats[g["label"]][1],
                          "f0": sonify.base_freq(g["label"], n), "color": sonify.COLOR_BY_PAIR.get(g["label"], "#999")}
                         for n, g in enumerate(ref["groups"])]
        ref["force"] = {"mean": 0.0, "std": 1.0}

        seg = frames(z, R[slice(*EXPLORE)])
        X, _ = sonify.features(seg, ref)
        freq, octaves = sonify.pitches(X, ref, GAIN)
        mp3(sonify.synthesize(freq, FPS), OUT / "audio" / f"md17_{key}.mp3")
        trajdata.write(OUT / "data" / "traj" / f"md17_{key}.json", name=name, numbers=z,
                       positions=R[slice(*EXPLORE)], ref=ref, octaves=octaves, fps=FPS,
                       extra={"audio": f"audio/md17_{key}.mp3", "source": "MD17, DFT AIMD at 500 K",
                              "frame0": EXPLORE[0]})
        index.append({"id": f"md17_{key}", "name": name, "voices": [g["label"] for g in ref["groups"]]})

        for q, start in enumerate(int(f * (len(R) - QUIZ_LEN)) for f in QUIZ_AT):
            seg = frames(z, R[start:start + QUIZ_LEN])
            X, _ = sonify.features(seg, ref)
            freq, _ = sonify.pitches(X, ref, GAIN)
            f = f"audio/quiz_{key}_{q}.mp3"
            mp3(sonify.synthesize(freq, FPS), OUT / f)
            quiz.append({"file": f, "answer": f"md17_{key}"})
        print(f"{name}: voices {[g['label'] for g in ref['groups']]}")

    random.Random(3).shuffle(quiz)
    (OUT / "data" / "md17_quiz.json").write_text(json.dumps({"molecules": index, "clips": quiz}, indent=1))


if __name__ == "__main__":
    main()
