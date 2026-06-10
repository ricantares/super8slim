# Super8 — AGENTS.md

## Venv
Repo root (`/home/super8`) **is** the venv. Binaries live in `./bin/`.  
Use `python3` directly (resolves to `./bin/python3`). No `pip install` needed for core deps.

## Two code generations

**Old (root-level, class `Lotteria`)**
- `lotteria.py`, `lottery_lib.py`, `superenalotto.py`, `superenalotto_run.py`, `superenalotto_test.py`
- Import: `from lotteria import Lotteria`
- Run: `python3 superenalotto.py`

**New (`superenalotto/` package, v0.1.0)**
- `superenalotto/src/{collector,common_lib,stats_lib,forecast}.py`
- Import: relative within `superenalotto/src/`
- Run as module: `python3 superenalotto/src/collector.py ...`

## Main CLI — Collector
```bash
python3 superenalotto/src/collector.py data/estrazioni_2023.csv \
  --history-size 200 --sample-size 15 -o results.json
```
`--sample-size`: `15|30|60|90|all` (default `15`)  
`--threaded` / `--workers N` for parallel runs  
`--profile` for cProfile dump  
Log file: `superenalotto/analisi_statistiche.log`

## Data format
Semicolon CSV with header `Data estrazione;e1;e2;e3;e4;e5;e6`.  
Dates in `YYYYMMDD`. Numbers 1–90.  
Loaded via `np.loadtxt(..., delimiter=';', skiprows=1, usecols=(1,2,3,4,5,6))`.

## Tests
- `pytest test_lotteria.py` (has hardcoded path `/home/rromiti/super8/sw/data/...` — will fail elsewhere)
- Jupyter notebooks under `superenalotto/test/`: `testforecast.ipynb`, `testoccurrences.ipynb`, etc.
- `benchmark_sequences.py` — compares two sequence-counting implementations

## Other scripts
```bash
python3 scripts/fit_gmm.py --csv data/estrazioni_2026_2006.csv --n_components 6
python3 scripts/probability_demo.py --point 1,2,3,4,5,6  # --skip-autoencoder if no TF
```

## Dependencies (core)
numpy, scipy, pandas (pre-installed in venv).  
sklearn, tensorflow needed only for `scripts/*` (GMM / autoencoder).

## Lint / typecheck / formatter
None configured. Do not attempt.
