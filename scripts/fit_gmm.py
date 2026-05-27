#!/usr/bin/env python3
"""
Fit a Gaussian Mixture Model to 6D vectors stored in a semicolon-separated CSV.

Usage:
  python3 scripts/fit_gmm.py --csv data/estrazioni_2026_2006.csv --n_components 6

Saves model with joblib if --output is provided.
"""
import argparse
import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture


def load_csv_as_H(path):
    # CSV format: header 'Data estrazione;e1;e2;e3;e4;e5;e6'
    df = pd.read_csv(path, sep=';', engine='python')
    expected = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6']
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}")
    H = df[expected].to_numpy(dtype=float)
    return H


def fit_gmm(H, n_components=3, cov_type='full', random_state=0, max_iter=200):
    gmm = GaussianMixture(n_components=n_components, covariance_type=cov_type,
                          random_state=random_state, max_iter=max_iter)
    gmm.fit(H)
    return gmm


def main(argv=None):
    p = argparse.ArgumentParser(description='Fit GMM to 6D points CSV')
    p.add_argument('--csv', required=True, help='Path to semicolon CSV')
    p.add_argument('--n_components', type=int, default=3)
    p.add_argument('--cov_type', default='full', choices=['full', 'tied', 'diag', 'spherical'])
    p.add_argument('--random_state', type=int, default=0)
    p.add_argument('--output', help='Path to save fitted model (pickle)')
    p.add_argument('--max_iter', type=int, default=200)
    args = p.parse_args(argv)

    csv_path = args.csv
    if not os.path.exists(csv_path):
        print(f'CSV not found: {csv_path}', file=sys.stderr)
        sys.exit(2)

    H = load_csv_as_H(csv_path)
    print(f'Loaded H with shape {H.shape}')

    gmm = fit_gmm(H, n_components=args.n_components, cov_type=args.cov_type,
                  random_state=args.random_state, max_iter=args.max_iter)

    # Diagnostics
    ll = gmm.score(H)
    per_sample_ll = gmm.score_samples(H)
    print(f'Average log-likelihood (per sample): {ll:.4f}')
    print(f'AIC: {gmm.aic(H):.1f}  BIC: {gmm.bic(H):.1f}')
    print('\nWeights:')
    print(gmm.weights_)
    print('\nMeans:')
    print(gmm.means_)
    print('\nCovariances:')
    print(gmm.covariances_)

    if args.output:
        outdir = os.path.dirname(args.output)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        with open(args.output, 'wb') as f:
            pickle.dump(gmm, f)
        print(f'Saved model to {args.output}')

    # Example: sample 10 new points and print them
    samples, comp = gmm.sample(10)
    print('\nExample samples (10):')
    print(samples)


if __name__ == '__main__':
    main()
