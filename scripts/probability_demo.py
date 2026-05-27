#!/usr/bin/env python3
"""Demo script to fit models and score a new 6D point."""

import argparse
import os
import sys

import numpy as np
import pandas as pd

# Make sure repository root is importable when running as a script.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.probability_estimates import (
    fit_pca,
    pca_probability,
    gmm_probability,
    gmm_responsibilities,
    fit_autoencoder,
    autoencoder_probability,
)


def load_points(csv_path):
    df = pd.read_csv(csv_path, sep=';')
    expected = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6']
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f'Missing expected columns: {missing}')
    return df[expected].to_numpy(dtype=float)


def parse_point(value):
    parts = value.split(',')
    if len(parts) != 6:
        raise argparse.ArgumentTypeError('Point must be 6 comma-separated integers')
    return np.array([int(x.strip()) for x in parts], dtype=float)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Fit models and score a 6D point')
    parser.add_argument('--csv', default='data/estrazioni_2026_2006.csv', help='CSV file with columns e1..e6')
    parser.add_argument('--point', type=parse_point, default='1,2,3,4,5,6', help='Point as 6 comma-separated ints')
    parser.add_argument('--pca-k', type=int, default=3, help='PCA latent dimension')
    parser.add_argument('--gmm-components', type=int, default=6, help='GMM component count')
    parser.add_argument('--ae-latent-dim', type=int, default=3, help='Autoencoder latent dimension')
    parser.add_argument('--ae-epochs', type=int, default=50, help='Autoencoder training epochs')
    parser.add_argument('--skip-autoencoder', action='store_true', help='Skip autoencoder training')
    args = parser.parse_args(argv)

    csv_path = args.csv
    if not os.path.exists(csv_path):
        raise SystemExit(f'CSV file not found: {csv_path}')

    H = load_points(csv_path)
    p = args.point.astype(float).reshape(1, -1)
    print('Loaded', H.shape, 'points from', csv_path)
    print('Query point:', p.flatten().tolist())
    print('---')

    # PCA
    pca, noise_var = fit_pca(H, k=args.pca_k)
    pca_score = pca_probability(p, pca, noise_var)
    print(f'PCA score (k={args.pca_k}, noise_var={noise_var:.4g}): {pca_score:.6g}')

    # GMM
    from sklearn.mixture import GaussianMixture
    gmm = GaussianMixture(n_components=args.gmm_components, covariance_type='full', random_state=0)
    gmm.fit(H)
    gmm_density = gmm_probability(p, gmm)
    gmm_resp = gmm_responsibilities(p, gmm)
    print(f'GMM density (components={args.gmm_components}): {gmm_density:.6g}')
    print('GMM responsibilities:', np.round(gmm_resp, 6).tolist())

    # Autoencoder
    if args.skip_autoencoder:
        print('Autoencoder skipped.')
        return

    try:
        ae = fit_autoencoder(H, latent_dim=args.ae_latent_dim, epochs=args.ae_epochs, batch_size=32, verbose=0)
        ae_score = autoencoder_probability(p, ae['encoder'], ae['decoder'], noise_var=ae['reconstruction_mse'])
        print(f'Autoencoder score (latent={args.ae_latent_dim}): {ae_score:.6g}')
        print(f'Autoencoder training MSE: {ae["reconstruction_mse"]:.6g}')
    except ImportError as exc:
        print('Autoencoder skipped: TensorFlow is not installed.')
        print(exc)
    except Exception as exc:
        print('Autoencoder failed:', exc)


if __name__ == '__main__':
    main()
