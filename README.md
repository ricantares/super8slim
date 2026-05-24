# Super8 - SuperEnalotto Analysis System

A Python-based system for analyzing Italian SuperEnalotto lottery data, studying historical patterns, and generating statistical insights.

## Technical
### Dockerfile
    # Usa l'immagine ufficiale di Ubuntu 24.04.2 LTS come base
    FROM ubuntu:24.04

    # Imposta variabile di ambiente per non interattività durante l'installazione
    ENV DEBIAN_FRONTEND=noninteractive

    # Aggiorna la lista pacchetti e installa Python 3 e pip
    RUN apt-get update && \
        apt-get install -y python3 python3-pip && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

    # Imposta python3 come comando python di default
    RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

    # Verifica versione Python (opzionale)
    RUN python --version

    # Comando di default all'avvio del container (puoi modificarlo)
    CMD ["python3"]

### Python infos
    - Python 3.12.3
    - pip 24.0 (Python 3.12)
    - numpy 2.2.6
    - scipy 1.17.0
    - pandas 2.2.3

    Venv
    /home/super8

## Overview

This codebase provides tools for:
- Loading and analyzing historical SuperEnalotto draw data
- Computing combination frequencies across different draw classes
- Generating statistical rules from historical patterns
- Testing predictions against non-training data sets

## Project Structure

```
super8/
├── Core Modules
│   ├── lotteria.py          # Main Lotteria class with core functionality
│   ├── lottery_lib.py      # Helper functions for lottery operations
│   └── superenalotto.py    # Historical data analysis & rule generation
│
├── Execution Scripts
│   ├── superenalotto_run.py # Run analysis on test sets
│   ├── superenalotto_test.py
│   └── LotteryAi.py
│
├── Data Files
│   └── data/
│       ├── estrazioni_2023.csv     # Historical draws (2023)
│       ├── estrazioni_2026_2006.csv # Extended historical data
│       ├── Presenze_*.csv          # Presence statistics
│       └── Ritardi_*.csv           # Delay/latency data
│
├── Analysis Tools
│   ├── sequence_counter.py    # Count sequences in data
│   ├── benchmark_sequences.py
│   ├── sum_sommari_filtered.py
│   └── rebase_lib.py
│
└── Notebooks
    ├── calcolivari.ipynb
    ├── prove.ipynb
    └── rebase*.ipynb
```

## Key Concepts

### SuperEnalotto
Italian national lottery game where 6 numbers are drawn from 1-90 range.

### Core Classes

**Lotteria** (`lotteria.py`)
- Loads historical draw data from CSV files
- Generates random draws (6 numbers, 1-90, no duplicates)
- Computes combination frequencies
- Analyzes sequences across historical data

**Key Methods:**
- `genera_estrazione()` - Generate random 6-number draw
- `freq_combinazioni()` - Calculate combination frequencies
- `carica_storico()` - Load historical data

### Analysis Flow

1. **Data Loading** - Historical draws loaded from CSV (date + 6 numbers)
2. **Combination Analysis** - Analyze all k-combinations (k=1..6) from each draw
3. **Frequency Calculation** - Compute mean frequency across historical blocks
4. **Rule Generation** - Create statistical rules stored in JSON

## Usage

```python
from lotteria import Lotteria

# Initialize with historical data
ll = Lotteria("data/estrazioni_2023.csv")

# Generate random draw
estrazione = ll.genera_estrazione()

# Analyze combinations
freq = ll.freq_combinazioni(estrazione, 0, 90)
```

## Collector Usage

The collector script can analyze historical draw data and save JSON statistics.

```bash
python3 superenalotto/src/collector.py data/estrazioni_2023.csv \
  --history-size 200 \
  --sample-size 15 \
  -o results.json
```

### CLI options
- `--history-size`: number of historical draws to load (default: all)
- `--sample-size`: sample size to use for occurrence analysis; valid values: `15`, `30`, `60`, `90`, `all`
- `--workers`: number of parallel workers to use for independent collections
- `--threaded`: use `ThreadPoolExecutor` instead of `ProcessPoolExecutor` for parallel collection
- `--profile`: run the collector under `cProfile`
- `--profile-output`: file to write profiling data (default: `collector.prof`)
- `--profile-top`: number of top functions to print from profiling output

### Example threaded run

```bash
python3 superenalotto/src/collector.py data/estrazioni_2023.csv \
  --history-size 200 \
  --sample-size 15 \
  --threaded \
  --workers 4 \
  -o results_threaded.json
```

### Example profiling run

```bash
python3 superenalotto/src/collector.py data/estrazioni_2023.csv \
  --history-size 200 \
  --sample-size 15 \
  --profile \
  --profile-output /tmp/collector.prof
```

## Data Format

### Draws CSV
```csv
Data estrazione;e1;e2;e3;e4;e5;e6
20230415;7;22;36;52;79;86
```

- Column 1: Draw date (YYYYMMDD)
- Columns 2-7: The 6 drawn numbers (1-90)

## Dependencies

- `numpy` - Numerical computing
- `scipy` - Scientific computing (combinations)
- `pandas` - Data manipulation

## Version

- Current: 1.3 (as of October 2023)
- Initial release: October 2023