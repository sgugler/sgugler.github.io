# mol-sounds

Pilot: can a human hear a machine-learned force field fail in MD before the
automated checks catch it? The page lives at <https://sgugler.ch/mol-sounds/>.

```sh
conda activate base                       # numpy, ASE, scipy, matplotlib
python prepare.py                         # ~/Research/qcml/hdf5 -> data/*.extxyz
python baseline.py data/*.extxyz -o results/baseline.json
python sonify.py ref data/stable_300K.extxyz -o results/ref_stats.json
python sonify.py wav data/fail_400K.extxyz --ref results/ref_stats.json --gain 0.5 --fps 25 -o fail.wav
python build_site.py                      # glyceraldehyde audio, blind clips, animation JSON
python build_md17.py                      # MD17 tracks, animation JSON, quiz clips (data/md17/*.npz)
python build_chords.py                    # xtb spectra + graph spectra for the chords tab
python evaluate.py results/listeners/*.json
```

The page (`../static/mol-sounds/`) is plain HTML + ES modules: `viewer.js`
(canvas ball-and-stick viewer), `md.js` (explore with animation, blind
failure test, which-molecule quiz), `chords.js` (WebAudio chord/arpeggio from
vibrational or bond-graph spectra, with the mode animated).

- `build_md17.py`: MD17 (DFT AIMD, 500 K) for 8 molecules downloaded from
  quantum-machine.org; one fixed note per element pair (`sonify.BASE_BY_PAIR`)
  and voice statistics pooled over all molecules, so molecules are comparable.
- `build_chords.py`: RDKit embedding -> xtb `--ohess tight` (imaginary modes
  are followed downhill and re-optimised); graph mode is √λ of the
  mass-weighted, bond-order-weighted graph Laplacian scaled so X–H sits at
  3000 cm⁻¹.

- `sonify.py`: bonds from the reference's first frame, grouped by element pair
  into up to `--k` voices (max deviation per group), pitch
  `f0 * 2**(c (x - mean)/std)` clipped to −2…+3 octaves, continuous-phase
  sines, fixed soft limiter, optional `--force-loudness`. Writes 44.1 kHz WAV
  with `scipy.io.wavfile` (`soundfile` is not installed in base).
- `baseline.py`: first frame where energy drift > 0.5 eV, max force > 5 eV/Å
  or min distance < 0.75 Å.
- `build_site.py`: explore tracks and the 11 blind clips; answer key in
  `static/mol-sounds/data/key.json`.
- `evaluate.py`: delay per failing clip and false-alarm rate from the JSON
  files the page lets listeners download; plot of human vs automated frame.

Data: glyceraldehyde, one SchNetPack model (2024-3-19_d9b81aac), NVE velocity
Verlet 0.5 fs, same start geometry; 300 K × 2000 steps (stable, reference),
300 K × 20000 steps (stable, extra clips), 400 K × 2000 steps (fails; flagged
at frame 333). `data/` is not committed.

Known confound: the 400 K run is hotter from the start, so it sounds different
before it fails. A same-temperature stable run (e.g. a second 400 K seed that
survives, generated on the cluster with
`apptainer run --nv container.sif python md.py`) would remove that.
