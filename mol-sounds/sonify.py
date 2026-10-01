#!/usr/bin/env python3
"""Turn an MD trajectory into sound.

Bonds are detected once, in the first frame of the reference (stable)
trajectory, with ASE's natural cutoffs. For every frame, each bond's
deviation from its reference mean length is computed; bonds are grouped by
element pair and each group becomes one voice whose feature is the largest
absolute deviation in the group. Voice i sounds at

    f_i(t) = f0_i * 2 ** (c * (x_i(t) - mean_i) / std_i)

with mean_i, std_i the feature statistics in the reference trajectory and c
the gain in octaves per standard deviation. Sines are synthesised with
continuous phase, summed and soft-limited. Optionally the loudness follows
the maximum atomic force.

Two steps:
  python sonify.py ref data/stable_300K.extxyz -o results/ref_stats.json [--k 6]
  python sonify.py wav data/fail_400K.extxyz --ref results/ref_stats.json -o fail.wav \
      [--gain 0.5] [--fps 25] [--start 0 --stop 2001] [--force-loudness 0.0]
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from ase.io import read
from ase.neighborlist import natural_cutoffs, neighbor_list
from scipy.io import wavfile

warnings.filterwarnings("ignore")

SR = 44100
# Just-intonation chord on A3, all within ~200-800 Hz.
BASE_FREQS = [220.0, 275.0, 330.0, 440.0, 550.0, 660.0, 770.0, 385.0]
OCTAVE_CLIP = (-2.0, 3.0)  # keep pitches audible when a bond breaks


# ---------------------------------------------------------------- features
def detect_bonds(atoms, mult=1.15):
    i, j = neighbor_list("ij", atoms, natural_cutoffs(atoms, mult=mult))
    return sorted({(int(a), int(b)) for a, b in zip(i, j) if a < b})


def bond_lengths(frames, bonds):
    idx = np.asarray(bonds)
    pos = np.stack([a.positions for a in frames])  # (T, N, 3)
    return np.linalg.norm(pos[:, idx[:, 0]] - pos[:, idx[:, 1]], axis=-1)  # (T, B)


def groups_for(atoms, bonds, k):
    """Group bonds by element pair; if more than k pairs, merge the smallest groups."""
    sym = atoms.get_chemical_symbols()
    by = {}
    for n, (a, b) in enumerate(bonds):
        key = "-".join(sorted((sym[a], sym[b]), key=lambda s: (s != "C", s)))
        by.setdefault(key, []).append(n)
    groups = sorted(by.items(), key=lambda kv: -len(kv[1]))
    while len(groups) > k:
        (n1, b1), (n2, b2) = groups[-2], groups[-1]
        groups = groups[:-2] + [(f"{n1}+{n2}", b1 + b2)]
    return [{"label": name, "bonds": idx} for name, idx in groups]


def voice_features(lengths, bond_eq, groups):
    dev = np.abs(lengths - bond_eq[None, :])
    return np.stack([dev[:, g["bonds"]].max(axis=1) for g in groups], axis=1)  # (T, k)


def max_force(frames):
    return np.array([np.linalg.norm(a.get_forces(), axis=1).max() for a in frames])


# ---------------------------------------------------------------- reference
def make_ref(path, k):
    frames = read(path, ":")
    bonds = detect_bonds(frames[0])
    L = bond_lengths(frames, bonds)
    bond_eq = L.mean(axis=0)
    groups = groups_for(frames[0], bonds, k)
    X = voice_features(L, bond_eq, groups)
    F = max_force(frames)
    sym = frames[0].get_chemical_symbols()
    return {
        "source": str(path),
        "bonds": bonds,
        "bond_labels": [f"{sym[a]}{a}-{sym[b]}{b}" for a, b in bonds],
        "bond_eq": bond_eq.tolist(),
        "groups": [
            {**g, "mean": float(X[:, n].mean()), "std": float(X[:, n].std()), "f0": BASE_FREQS[n]}
            for n, g in enumerate(groups)
        ],
        "force": {"mean": float(F.mean()), "std": float(F.std())},
    }


# ---------------------------------------------------------------- synthesis
def features(frames, ref):
    L = bond_lengths(frames, [tuple(b) for b in ref["bonds"]])
    X = voice_features(L, np.asarray(ref["bond_eq"]), ref["groups"])
    return X, max_force(frames)


def pitches(X, ref, gain):
    mean = np.array([g["mean"] for g in ref["groups"]])
    std = np.array([g["std"] for g in ref["groups"]])
    f0 = np.array([g["f0"] for g in ref["groups"]])
    octaves = np.clip(gain * (X - mean) / std, *OCTAVE_CLIP)
    return f0 * 2.0**octaves, octaves


def synthesize(freq, fps, force_z=None, force_gain=0.0):
    """freq: (T, k) Hz per frame. Returns float32 mono audio."""
    T, k = freq.shape
    n = int(round(T / fps * SR))
    t_frames = np.arange(T) / fps
    t_audio = np.arange(n) / SR
    out = np.zeros(n)
    for v in range(k):
        f = np.interp(t_audio, t_frames, freq[:, v])
        phase = 2 * np.pi * np.cumsum(f) / SR
        out += np.sin(phase) * (0.8 / k)
    if force_z is not None and force_gain:
        env = np.clip(1.0 + force_gain * np.interp(t_audio, t_frames, force_z), 0.25, 4.0)
        out *= env
    out = np.tanh(1.5 * out) / np.tanh(1.5)  # fixed soft limiter, no per-file normalisation
    fade = min(n // 2, int(0.02 * SR))
    ramp = np.linspace(0, 1, fade)
    out[:fade] *= ramp
    out[-fade:] *= ramp[::-1]
    return out.astype(np.float32)


def render(path, ref, gain=0.5, fps=25.0, start=0, stop=None, force_gain=0.0):
    frames = read(path, f"{start}:{'' if stop is None else stop}")
    X, F = features(frames, ref)
    freq, octaves = pitches(X, ref, gain)
    fz = (F - ref["force"]["mean"]) / ref["force"]["std"]
    audio = synthesize(freq, fps, fz, force_gain)
    return audio, {"features": X, "octaves": octaves, "force": F}


def write_wav(path, audio):
    wavfile.write(path, SR, (np.clip(audio, -1, 1) * 32767).astype(np.int16))


# ---------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("ref", help="compute reference statistics from a stable trajectory")
    r.add_argument("traj")
    r.add_argument("--k", type=int, default=6, help="max number of voices (default 6)")
    r.add_argument("-o", "--out", required=True)
    w = sub.add_parser("wav", help="sonify a trajectory")
    w.add_argument("traj")
    w.add_argument("--ref", required=True)
    w.add_argument("--gain", type=float, default=0.5, help="c, octaves per std (default 0.5)")
    w.add_argument("--fps", type=float, default=25.0, help="MD frames per second of audio (default 25)")
    w.add_argument("--start", type=int, default=0)
    w.add_argument("--stop", type=int, default=None)
    w.add_argument("--force-loudness", type=float, default=0.0, help="loudness gain per force std (default 0: off)")
    w.add_argument("-o", "--out", required=True)
    a = p.parse_args()

    if a.cmd == "ref":
        ref = make_ref(a.traj, a.k)
        Path(a.out).write_text(json.dumps(ref, indent=1))
        for g in ref["groups"]:
            print(f"voice {g['label']:8s} {len(g['bonds']):2d} bonds  f0 {g['f0']:.0f} Hz  mean {g['mean']:.4f} Å  std {g['std']:.4f} Å")
    else:
        ref = json.loads(Path(a.ref).read_text())
        audio, _ = render(a.traj, ref, a.gain, a.fps, a.start, a.stop, a.force_loudness)
        write_wav(a.out, audio)
        print(f"{a.out}: {len(audio) / SR:.1f} s")


if __name__ == "__main__":
    main()
