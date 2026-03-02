"""
Benchmark: compare running time of
  - count_sequences()  (sequence_counter.py  – numpy-based)
  - freq_sequenze()    (lotteria.py           – loop-based, method of Lotteria)

Usage:
    python benchmark_sequences.py
"""

import timeit
import random
import numpy as np

from sequence_counter import count_sequences
from lotteria import Lotteria


# ── helpers ──────────────────────────────────────────────────────────────────

def random_draw():
    """Return a sorted numpy array of 6 distinct integers in [1, 90]."""
    return np.array(sorted(random.sample(range(1, 91), 6)))


def build_dataset(n: int) -> list[np.ndarray]:
    """Build *n* random lottery draws."""
    return [random_draw() for _ in range(n)]


# ── wrappers that accept the same plain draw ──────────────────────────────────

# Lotteria instance (no file needed – we only call freq_sequenze which doesn't
# touch the historical data)
_lotteria = Lotteria()


def run_count_sequences(dataset):
    for draw in dataset:
        count_sequences(draw)


def run_freq_sequenze(dataset):
    for draw in dataset:
        _lotteria.freq_sequenze(draw)


# ── benchmark ─────────────────────────────────────────────────────────────────

def benchmark(n_draws: int = 10_000, n_repeat: int = 5) -> None:
    print(f"\n{'='*60}")
    print(f"  Benchmark – {n_draws:,} draws × {n_repeat} repetitions")
    print(f"{'='*60}\n")

    dataset = build_dataset(n_draws)

    # --- count_sequences ---
    t_count = timeit.repeat(
        stmt=lambda: run_count_sequences(dataset),
        number=1,
        repeat=n_repeat,
    )

    # --- freq_sequenze ---
    t_freq = timeit.repeat(
        stmt=lambda: run_freq_sequenze(dataset),
        number=1,
        repeat=n_repeat,
    )

    best_count = min(t_count)
    best_freq  = min(t_freq)
    ratio      = best_freq / best_count if best_count > 0 else float("inf")

    col = 28
    print(f"  {'Function':<{col}} {'min (s)':>10}  {'avg (s)':>10}  {'max (s)':>10}")
    print(f"  {'-'*col}  {'-'*10}  {'-'*10}  {'-'*10}")
    print(f"  {'count_sequences()':<{col}} {min(t_count):>10.4f}  "
          f"{sum(t_count)/n_repeat:>10.4f}  {max(t_count):>10.4f}")
    print(f"  {'freq_sequenze()':<{col}} {min(t_freq):>10.4f}  "
          f"{sum(t_freq)/n_repeat:>10.4f}  {max(t_freq):>10.4f}")
    print()
    print(f"  Speed-up  count_sequences vs freq_sequenze : {ratio:.2f}×")

    if ratio > 1:
        print(f"  → count_sequences() is {ratio:.2f}× FASTER than freq_sequenze()")
    elif ratio < 1:
        inv = 1 / ratio
        print(f"  → freq_sequenze() is {inv:.2f}× FASTER than count_sequences()")
    else:
        print("  → Both functions have the same speed.")

    print(f"\n{'='*60}\n")

    # ── per-draw sanity check: show results on the same sample draws ──────────
    print("  Sanity check on 5 sample draws:\n")
    samples = build_dataset(5)
    print(f"  {'Draw':<30} {'count_sequences':>30}  {'freq_sequenze':>30}")
    print(f"  {'-'*30}  {'-'*30}  {'-'*30}")
    for draw in samples:
        cs = count_sequences(draw)
        fs = _lotteria.freq_sequenze(draw)
        print(f"  {str(draw.tolist()):<30}  {str(cs):>30}  {str(fs):>30}")
    print()


if __name__ == "__main__":
    benchmark(n_draws=10_000, n_repeat=5)
