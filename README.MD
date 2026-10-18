# SuperEnalotto Statistical Analysis

This project analyzes historical SuperEnalotto draws to compute statistical patterns and generate forecast combinations. It focuses on the analysis of number occurrence, sequence frequency, delays, bounds, and row-sum behavior across historical extractions.

The code is organized as a small Python package under `superenalotto/` and is designed to work with a historical CSV dataset of past SuperEnalotto results.

## Project goal

The main objective is to study how numbers and combinations behave over time, then use those statistics to suggest candidate draws that respect the historical constraints extracted from previous data.

The project is built around two main phases:

1. Data collection and statistical profiling
2. Forecast generation based on historical bounds and validity rules

## Main features

- Loads SuperEnalotto historical extractions from CSV
- Computes occurrence statistics by combination class
- Analyzes sequences, delays, and bounds
- Evaluates row-sum behavior
- Generates forecast combinations that respect the learned statistical bounds
- Stores analysis results in JSON and CSV outputs
- Supports parallel processing for heavier computation workloads

## Repository structure

```text
super8/
├── Containerfile
├── build.txt
├── requirements.txt
├── README.MD
├── superenalotto/
│   ├── __init__.py
│   ├── config.ini
│   ├── analisi_statistiche.log
│   ├── collector_results.json
│   ├── forecast.csv
│   ├── data/
│   │   └── estrazioni_2026_2006_copy.csv
│   └── src/
│       ├── __init__.py
│       ├── common_lib.py
│       ├── collector.py
│       ├── forecast.py
│       └── stats_lib.py
└── test/
    └── notebooks for experimental checks
```

## Dependencies

The project uses:

- Python 3.15 (as defined in `Containerfile`)
- NumPy
- SciPy

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Setup

### Option 1: local Python environment

Make sure Python 3.15 is available on your system, then install the required dependencies.

```bash
cd super8
pip install -r requirements.txt
```

### Option 2: containerized environment

The repository includes a `Containerfile` configured for a slim Python image. The helper file `build.txt` contains the commands used to build and run the project in a WSL/container workflow.

Example:

```bash
wslc build -t python-sup8 .
wslc run -it --rm -v "${PWD}\superenalotto:/app/superenalotto" python-sup8 bash
```

## Data format

The project expects historical lottery data as a CSV file with 7 columns:

- date
- number 1
- number 2
- number 3
- number 4
- number 5
- number 6

The file under `superenalotto/data/estrazioni_2026_2006_copy.csv` follows this structure and is consumed by the loader in `common_lib.py`.

## Data collection

The collector script analyzes historical draw data and computes several categories of statistical results.

Run it with:

```bash
python superenalotto/src/collector.py superenalotto/data/estrazioni_2026_2006_copy.csv -o superenalotto/collector_results.json --sample-size 15
```

Available collector options:

- `--sample-size` can be `15`, `30`, `60`, `90`, or `all`
- `--history-size` limits how many historical rows are loaded
- `--workers` configures parallel execution
- `--threaded` uses a thread-based executor instead of a process pool

The collector writes a JSON file containing grouped data such as:

- `occurrences`
- `sequences`
- `delays`
- `bounds`
- `row_sums`

## Forecast generation

The forecast module reads the previously generated stats and creates candidate combinations according to the learned bounds.

Example:

```bash
python superenalotto/src/forecast.py --input_file superenalotto/data/estrazioni_2026_2006_copy.csv --stats superenalotto/collector_results.json --forecast_number 10
```

The generated output is saved as `superenalotto/forecast.csv` by default, as defined in `config.ini`.

## Configuration

The project configuration is stored in `superenalotto/config.ini`.

Key settings include:

```ini
[logging]
log_file = analisi_statistiche.log
log_level = DEBUG

[forecast]
forecast_directives = collector_results.json
forecast_combinations_number = 10
forecast_output_file = forecast.csv

[hystorical_data]
data_file = data/estrazioni_2026_2006_copy.csv
```

## Statistical logic

The analysis is based on a set of metrics that evaluate how past draws relate to one another. In particular, the project calculates:

- occurrence frequency of combinations
- appearance patterns across sample windows
- delays between repeated values or combinations
- numerical bounds and data distribution behavior
- row sums to detect aggregate tendencies

This is an experimental statistical approach, not a guaranteed prediction system. It is best used as a research or exploratory tool for lottery draw analysis.

## Notes

- The repository contains experimental notebooks in `superenalotto/test/` for testing and exploration.
- The project is primarily a research-oriented tool, not a production-ready betting engine.
- The code uses direct file-based processing and a custom statistical pipeline rather than a library-based forecasting framework.

## License

This project does not currently declare a formal license file. Please check the repository owner or maintainers before redistributing or using it in production environments.
