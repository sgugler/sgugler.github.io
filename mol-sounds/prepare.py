#!/usr/bin/env python3
"""Convert the glyceraldehyde MD runs into extxyz files with energies and forces.

Sources (all SchNetPack model 2024-3-19_d9b81aac, NVE velocity Verlet, 0.5 fs,
same starting geometry):
  stable_300K   glyceraldehyde_md.traj             2001 frames, energies + forces
  fail_400K     glyceraldehyde_2000_400K_md.traj   2001 frames, energies + forces
  long_300K     glyceraldehyde_20000.hdf5          20001 frames, energies + forces

The kinetic energy is stored in atoms.info["kinetic_energy"] (the .traj files
have no momenta), so the total energy is Epot + that value.

Usage: python prepare.py [--src ~/Research/qcml/hdf5] [--out data]
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.io import read, write

warnings.filterwarnings("ignore")


def from_traj(path):
    frames = read(path, ":")
    out = []
    for a in frames:
        b = Atoms(a.numbers, positions=a.positions)
        b.info["kinetic_energy"] = float(a.info["kinetic_energy"])
        b.calc = SinglePointCalculator(b, energy=a.get_potential_energy(), forces=a.get_forces())
        out.append(b)
    return out


def from_hdf5(path):
    import h5py

    with h5py.File(path) as h:
        steps = sorted(h["positions"].keys(), key=int)
        numbers = np.asarray(h["numbers"][steps[0]]).ravel()
        out = []
        for s in steps:
            pos = np.asarray(h["positions"][s]).reshape(-1, 3)
            frc = np.asarray(h["forces"][s]).reshape(-1, 3)
            b = Atoms(numbers, positions=pos)
            b.info["kinetic_energy"] = float(np.asarray(h["kinetic_energy"][s]).ravel()[0])
            epot = float(np.asarray(h["potential_energy"][s]).ravel()[0])
            b.calc = SinglePointCalculator(b, energy=epot, forces=frc)
            out.append(b)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--src", default=str(Path.home() / "Research/qcml/hdf5"))
    p.add_argument("--out", default=str(Path(__file__).parent / "data"))
    a = p.parse_args()
    src, out = Path(a.src), Path(a.out)
    out.mkdir(exist_ok=True)
    jobs = {
        "stable_300K": (from_traj, src / "glyceraldehyde_md.traj"),
        "fail_400K": (from_traj, src / "glyceraldehyde_2000_400K_md.traj"),
        "long_300K": (from_hdf5, src / "glyceraldehyde_20000.hdf5"),
    }
    for name, (fn, path) in jobs.items():
        frames = fn(path)
        write(out / f"{name}.extxyz", frames)
        print(f"{name}: {len(frames)} frames -> {out / (name + '.extxyz')}")


if __name__ == "__main__":
    main()
