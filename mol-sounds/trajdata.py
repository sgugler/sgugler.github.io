"""Per-trajectory JSON for the page: aligned positions, bonds, voices, pitches."""
import json

import numpy as np


def kabsch_align(pos):
    """Remove centre of mass drift and rotation relative to the first frame. pos: (T, N, 3)."""
    pos = pos - pos.mean(axis=1, keepdims=True)
    ref = pos[0]
    out = np.empty_like(pos)
    for t, p in enumerate(pos):
        h = p.T @ ref
        u, _, vt = np.linalg.svd(h)
        d = np.sign(np.linalg.det(vt.T @ u.T))
        r = vt.T @ np.diag([1, 1, d]) @ u.T
        out[t] = p @ r.T
    return out


def write(path, *, name, numbers, positions, ref, octaves, fps, extra=None):
    """positions (T, N, 3) Å; ref as produced by sonify.make_ref; octaves (T, k)."""
    group_of = {}
    for g, grp in enumerate(ref["groups"]):
        for b in grp["bonds"]:
            group_of[b] = g
    bonds = [[int(i), int(j), group_of[n]] for n, (i, j) in enumerate(ref["bonds"])]
    aligned = kabsch_align(np.asarray(positions, float))
    data = {
        "name": name,
        "fps": fps,
        "frames": len(aligned),
        "Z": [int(z) for z in numbers],
        "bonds": bonds,
        "bond_eq": np.round(ref["bond_eq"], 4).tolist(),
        "groups": [{"label": g["label"], "f0": g["f0"], "std": round(g["std"], 5), "color": g.get("color", "#999")}
                   for g in ref["groups"]],
        "pos": np.round(aligned.reshape(len(aligned), -1), 3).tolist(),
        "octaves": np.round(np.asarray(octaves).T, 3).tolist(),
        **(extra or {}),
    }
    path.write_text(json.dumps(data, separators=(",", ":")))
    return data
