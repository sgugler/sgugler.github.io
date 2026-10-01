#!/usr/bin/env python3
"""Automated failure checks for an MD trajectory.

For each trajectory, report the first frame where any of these fires:
  energy  |E_tot(t) - E_tot(0)| > --e-thr   (eV)
  force   max_i |F_i(t)|        > --f-thr   (eV/Å)
  dist    min_ij r_ij(t)        < --d-thr   (Å)

E_tot = potential energy + atoms.info["kinetic_energy"].

Usage:
  python baseline.py data/fail_400K.extxyz [more.extxyz ...] -o results/baseline.json
"""
import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from ase.io import read

warnings.filterwarnings("ignore")


def series(frames):
    """Per-frame E_tot drift, max force norm and minimum distance."""
    etot, fmax, dmin = [], [], []
    for a in frames:
        try:
            e = a.get_potential_energy() + a.info.get("kinetic_energy", 0.0)
        except Exception:
            e = np.nan
        etot.append(e)
        fmax.append(float(np.linalg.norm(a.get_forces(), axis=1).max()))
        d = a.get_all_distances()
        np.fill_diagonal(d, np.inf)
        dmin.append(float(d.min()))
    etot = np.asarray(etot)
    return {"drift": np.abs(etot - etot[0]), "fmax": np.asarray(fmax), "dmin": np.asarray(dmin)}


def first(mask):
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else None


def check(s, e_thr, f_thr, d_thr):
    hits = {
        "energy": first(s["drift"] > e_thr),
        "force": first(s["fmax"] > f_thr),
        "dist": first(s["dmin"] < d_thr),
    }
    flagged = [v for v in hits.values() if v is not None]
    return {"first": min(flagged) if flagged else None, **hits}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("traj", nargs="+")
    p.add_argument("--e-thr", type=float, default=0.5, help="energy drift threshold, eV (default 0.5)")
    p.add_argument("--f-thr", type=float, default=5.0, help="max force threshold, eV/Å (default 5)")
    p.add_argument("--d-thr", type=float, default=0.75, help="min distance threshold, Å (default 0.75)")
    p.add_argument("-o", "--out", default=None)
    a = p.parse_args()

    report = {"thresholds": {"energy": a.e_thr, "force": a.f_thr, "dist": a.d_thr}, "trajectories": {}}
    for path in a.traj:
        s = series(read(path, ":"))
        r = check(s, a.e_thr, a.f_thr, a.d_thr)
        r["frames"] = len(s["fmax"])
        report["trajectories"][Path(path).stem] = r
        print(f"{Path(path).stem:14s} frames={r['frames']:6d} first={r['first']}  energy={r['energy']} force={r['force']} dist={r['dist']}"
              f"  (max drift {np.nanmax(s['drift']):.2f} eV, max F {s['fmax'].max():.1f} eV/Å, min d {s['dmin'].min():.2f} Å)")
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
