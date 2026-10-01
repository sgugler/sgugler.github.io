#!/usr/bin/env python3
"""Precompute the data for the "molecule chords" tab.

For each molecule (SMILES -> RDKit 3D embedding -> xtb GFN2 optimisation and
Hessian) two spectra are stored, both in wavenumbers so the page can map them
to pitch with one rule:

  3D     the harmonic vibrational frequencies and IR intensities from xtb,
         with the normal-mode displacements for the animation.
  graph  a ball-and-spring model of the bond graph alone: masses are the
         atomic masses, every bond is a spring with stiffness equal to its
         bond order (aromatic 1.5). The frequencies are the square roots of
         the eigenvalues of the mass-weighted graph Laplacian
         M^-1/2 L M^-1/2, scaled so a single bond to hydrogen (λ ≈ 1/m_H)
         sits at 3000 cm^-1 like a real C-H stretch. Eigenvectors are one
         amplitude per atom.

Writes ../static/mol-sounds/data/chords/<id>.json and index.json.
Requires rdkit and xtb on PATH.
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

OUT = Path(__file__).parent.parent / "static" / "mol-sounds" / "data" / "chords"
GRAPH_SCALE = 3000.0  # cm^-1 for sqrt(λ) = 1 (amu^-1/2)

MOLECULES = [
    ("water", "water", "O", "small"),
    ("ammonia", "ammonia", "N", "small"),
    ("methane", "methane", "C", "small"),
    ("co2", "carbon dioxide", "O=C=O", "small"),
    ("formaldehyde", "formaldehyde", "C=O", "small"),
    ("ethylene", "ethylene", "C=C", "small"),
    ("acetylene", "acetylene", "C#C", "small"),
    ("ethanol", "ethanol", "CCO", "MD17"),
    ("malonaldehyde", "malonaldehyde", "OC=CC=O", "MD17"),
    ("glyceraldehyde", "glyceraldehyde", "OCC(O)C=O", "this page"),
    ("benzene", "benzene", "c1ccccc1", "MD17"),
    ("toluene", "toluene", "Cc1ccccc1", "MD17"),
    ("naphthalene", "naphthalene", "c1ccc2ccccc2c1", "MD17"),
    ("uracil", "uracil", "O=c1cc[nH]c(=O)[nH]1", "MD17"),
    ("salicylic", "salicylic acid", "OC(=O)c1ccccc1O", "MD17"),
    ("aspirin", "aspirin", "CC(=O)Oc1ccccc1C(=O)O", "MD17"),
    ("paracetamol", "paracetamol", "CC(=O)Nc1ccc(O)cc1", "rMD17"),
    ("caffeine", "caffeine", "Cn1cnc2c1c(=O)n(C)c(=O)n2C", "classic"),
    ("glucose", "α-D-glucose", "OC[C@H]1O[C@H](O)[C@H](O)[C@@H](O)[C@@H]1O", "classic"),
]


def embed(smiles, seed=7):
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(m, randomSeed=seed)
    AllChem.MMFFOptimizeMolecule(m)
    return m


def parse_g98(text, n_atoms):
    freqs, ir, disp = [], [], []
    blocks = text.split("Frequencies --")[1:]
    for b in blocks:
        f = [float(x) for x in b.splitlines()[0].split()]
        i = [float(x) for x in re.search(r"IR Inten\s+--(.*)", b).group(1).split()]
        rows = b.split("Atom AN")[1].splitlines()[1 : 1 + n_atoms]
        nums = np.array([[float(x) for x in r.split()[2:]] for r in rows])  # (N, 3*k)
        for k in range(len(f)):
            freqs.append(f[k])
            ir.append(i[k])
            disp.append(nums[:, 3 * k : 3 * k + 3])
    coords = []
    for line in text.split("Standard orientation")[1].splitlines()[5 : 5 + n_atoms]:
        coords.append([float(x) for x in line.split()[3:6]])
    return np.array(freqs), np.array(ir), np.array(disp), np.array(coords)


def xtb_modes(mol):
    with tempfile.TemporaryDirectory() as d:
        Chem.MolToXYZFile(mol, os.path.join(d, "mol.xyz"))
        env = {**os.environ, "OMP_NUM_THREADS": "4", "OMP_STACKSIZE": "1G"}
        subprocess.run(["xtb", "mol.xyz", "--ohess", "tight"], cwd=d, env=env, check=True, capture_output=True)
        text = Path(d, "g98.out").read_text()
    return parse_g98(text, mol.GetNumAtoms())


def graph_modes(mol):
    n = mol.GetNumAtoms()
    L = np.zeros((n, n))
    for b in mol.GetBonds():
        i, j, w = b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble()
        L[i, j] -= w
        L[j, i] -= w
        L[i, i] += w
        L[j, j] += w
    m = np.array([a.GetMass() for a in mol.GetAtoms()])
    Mi = np.diag(1 / np.sqrt(m))
    lam, vec = np.linalg.eigh(Mi @ L @ Mi)
    keep = lam > 1e-8
    return GRAPH_SCALE * np.sqrt(lam[keep]), vec[:, keep].T, lam[keep]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for mid, name, smiles, group in MOLECULES:
        mol = embed(smiles)
        nu, ir, disp, coords = xtb_modes(mol)
        for attempt in range(4):  # follow an imaginary mode downhill and re-optimise
            neg = np.flatnonzero(nu < -10)
            if not neg.size:
                break
            d = disp[neg[0]]
            print(f"  {name}: imaginary mode {nu[neg[0]]:.0f} cm-1, displacing and re-optimising")
            conf = mol.GetConformer()
            for a, xyz in enumerate(coords + 0.4 * d / np.linalg.norm(d, axis=1).max()):
                conf.SetAtomPosition(a, xyz.tolist())
            nu, ir, disp, coords = xtb_modes(mol)
        real = nu > 10
        g_nu, g_vec, g_lam = graph_modes(mol)
        bonds = [[b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble()] for b in mol.GetBonds()]
        data = {
            "id": mid,
            "name": name,
            "smiles": smiles,
            "group": group,
            "formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
            "mass": round(Descriptors.MolWt(mol), 2),
            "Z": [a.GetAtomicNum() for a in mol.GetAtoms()],
            "xyz": np.round(coords, 3).tolist(),
            "bonds": bonds,
            "vib": [
                {"nu": round(float(f), 1), "ir": round(float(i), 2), "d": np.round(dv, 3).tolist()}
                for f, i, dv in zip(nu[real], ir[real], disp[real])
            ],
            "graph": [{"nu": round(float(f), 1), "v": np.round(v, 3).tolist()} for f, v in zip(g_nu, g_vec)],
        }
        (OUT / f"{mid}.json").write_text(json.dumps(data))
        index.append({"id": mid, "name": name, "group": group, "formula": data["formula"], "atoms": len(data["Z"]),
                      "modes": len(data["vib"])})
        print(f"{name:16s} {data['formula']:10s} {len(data['vib']):3d} vib modes {nu[real].min():6.0f}-{nu[real].max():6.0f} cm-1 | "
              f"graph {g_nu.min():5.0f}-{g_nu.max():5.0f} cm-1")
    (OUT / "index.json").write_text(json.dumps(index, indent=1))


if __name__ == "__main__":
    main()
