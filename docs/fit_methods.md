# Fitting 6D Point Clouds — PCA, GMM, Autoencoder

This document summarizes three ways to fit a function (or distribution) to a set of 6-dimensional integer points and includes runnable code snippets and usage notes. The repository also includes an executable GMM script at `scripts/fit_gmm.py` which is used on `data/estrazioni_2026_2006.csv`.

---

## Quick Install

Install required packages (use your virtualenv if you have one):

```bash
pip install numpy pandas scikit-learn
# Optional, for the autoencoder approach:
pip install tensorflow
```

---

## 1) PCA — Linear subspace approximation

When the points lie near a linear subspace, PCA finds the best low-dimensional affine approximation.

Snippet:

```python
import numpy as np
from sklearn.decomposition import PCA

def fit_pca(H, k=2):
    pca = PCA(n_components=k)
    Z = pca.fit_transform(H)
    def decoder(z):
        return pca.inverse_transform(z)
    def encoder(x):
        return pca.transform(x)
    return {'model': pca, 'encoder': encoder, 'decoder': decoder, 'Z': Z, 'explained_variance_ratio': pca.explained_variance_ratio_}

# Usage:
# H = np.loadtxt('data/estrazioni_2026_2006.csv', delimiter=';', skiprows=1, usecols=(1,2,3,4,5,6))
# p = fit_pca(H, k=3)
# recon = p['decoder'](p['encoder'](H))
```

Notes: choose `k` based on cumulative explained variance.

---

## 2) Gaussian Mixture Model (GMM) — probabilistic density and sampling

This models the empirical distribution as a mixture of Gaussians. Good for density estimation, clustering, and sampling new synthetic points.

The repository includes a ready script: `scripts/fit_gmm.py`.

How to run the script on the included CSV:

```bash
# fit a 6-component GMM and save the model (pickle)
python3 scripts/fit_gmm.py --csv data/estrazioni_2026_2006.csv --n_components 6 --output models/gmm_6.pkl
```

What the script does:
- loads `e1..e6` columns from the semicolon CSV
- fits `sklearn.mixture.GaussianMixture`
- prints average log-likelihood, AIC, BIC, weights, means, covariances
- saves model with `pickle` if `--output` is provided
- prints a small sample of generated points

Inline snippet (equivalent logic):

```python
import pandas as pd
from sklearn.mixture import GaussianMixture

df = pd.read_csv('data/estrazioni_2026_2006.csv', sep=';')
H = df[['e1','e2','e3','e4','e5','e6']].to_numpy(dtype=float)
gmm = GaussianMixture(n_components=6, covariance_type='full', random_state=0)
gmm.fit(H)
print('AIC', gmm.aic(H), 'BIC', gmm.bic(H))
samples, comps = gmm.sample(10)
```

When to choose GMM:
- You want a generative model or cluster structure.
- You need likelihood scores for points.

---

## Probability estimation for a new point

The following functions are implemented in `scripts/probability_estimates.py`.

- PCA: estimate a score from the reconstruction error of the projected point.
- GMM: use the model density directly via `score_samples`.
- Autoencoder: estimate a score from the reconstruction error of the decoded point.

```python
import numpy as np
from scripts.probability_estimates import (
    fit_pca,
    pca_probability,
    gmm_probability,
    gmm_responsibilities,
    fit_autoencoder,
    autoencoder_probability,
)

# PCA
H = np.loadtxt('data/estrazioni_2026_2006.csv', delimiter=';', skiprows=1, usecols=(1,2,3,4,5,6))
pca, noise_var = fit_pca(H, k=3)
p = np.array([1, 2, 3, 4, 5, 6])
print('PCA score:', pca_probability(p, pca, noise_var))

# GMM
import pandas as pd
from sklearn.mixture import GaussianMixture

df = pd.read_csv('data/estrazioni_2026_2006.csv', sep=';')
H = df[['e1','e2','e3','e4','e5','e6']].to_numpy(dtype=float)
gmm = GaussianMixture(n_components=6, covariance_type='full', random_state=0)
gmm.fit(H)
print('GMM density:', gmm_probability(p, gmm))
print('GMM responsibilities:', gmm_responsibilities(p, gmm))

# Autoencoder
ae = fit_autoencoder(H, latent_dim=3, epochs=100, batch_size=16, verbose=0)
print('Autoencoder score:', autoencoder_probability(p, ae['encoder'], ae['decoder'], noise_var=ae['reconstruction_mse']))
```

---

## 3) Autoencoder — Nonlinear manifold + decoder

Use a neural autoencoder when the point cloud sits on a nonlinear manifold and you want a parametric encoder/decoder.

Snippet (TensorFlow / Keras):

```python
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

def fit_autoencoder(H, latent_dim=2, epochs=200, batch_size=32, verbose=0):
    X = H.astype('float32')
    input_dim = X.shape[1]

    inp = layers.Input(shape=(input_dim,))
    x = layers.Dense(64, activation='relu')(inp)
    x = layers.Dense(32, activation='relu')(x)
    z = layers.Dense(latent_dim, activation=None, name='latent')(x)

    d = layers.Dense(32, activation='relu')(z)
    d = layers.Dense(64, activation='relu')(d)
    out = layers.Dense(input_dim, activation=None)(d)

    ae = models.Model(inputs=inp, outputs=out)
    encoder = models.Model(inputs=inp, outputs=z)

    latent_in = layers.Input(shape=(latent_dim,))
    dec_layer = ae.layers[-3](latent_in)
    dec_layer = ae.layers[-2](dec_layer)
    dec_out = ae.layers[-1](dec_layer)
    decoder = models.Model(inputs=latent_in, outputs=dec_out)

    ae.compile(optimizer=optimizers.Adam(1e-3), loss='mse')
    ae.fit(X, X, epochs=epochs, batch_size=batch_size, shuffle=True, verbose=verbose)

    def encode(x): return encoder.predict(np.asarray(x, dtype='float32'))
    def decode(zv): return decoder.predict(np.asarray(zv, dtype='float32'))

    recon = ae.predict(X)
    mse = np.mean(np.square(X - recon))
    return {'autoencoder': ae, 'encoder': encode, 'decoder': decode, 'reconstruction_mse': mse}

# Usage:
# ae = fit_autoencoder(H, latent_dim=3, epochs=100, batch_size=16, verbose=1)
# z = ae['encoder'](H[:5]); x_hat = ae['decoder'](z)
```

Notes: tune architecture, latent dim, and regularization for best results.

---

## Choosing among methods

- Use PCA for fast, interpretable linear compression.
- Use GMM for density modeling, clustering, and sampling.
- Use Autoencoder for flexible nonlinear manifolds when you need a parametric encoder/decoder.

---

## Files added / relevant

- `scripts/fit_gmm.py` — script to fit and save a `GaussianMixture` model from `data/estrazioni_2026_2006.csv`.
- `data/estrazioni_2026_2006.csv` — source CSV with `e1..e6` columns used as 6D points.

---

If you want, I can:
- run the `scripts/fit_gmm.py` here after you confirm installing the dependencies in this environment, or
- save the PCA and Autoencoder examples into runnable scripts and add small tests.

---

## Helper module for probability scoring

The file `scripts/probability_estimates.py` implements reusable scoring helpers for new 6D points:

- `fit_pca(H, k)` — fit PCA and estimate noise variance
- `pca_probability(p, pca, noise_var)` — score a point using PCA reconstruction error
- `gmm_probability(p, gmm)` — compute density from a fitted `GaussianMixture`
- `gmm_responsibilities(p, gmm)` — show per-component membership weights
- `fit_autoencoder(H, latent_dim, epochs, batch_size, verbose)` — fit an autoencoder
- `autoencoder_probability(p, encoder, decoder, noise_var)` — score an autoencoder reconstruction

You can use these helpers directly in your own Python workflow.

---

## Runnable example script

A ready demo script is available at `scripts/probability_demo.py`. It:

- loads `data/estrazioni_2026_2006.csv`
- fits PCA and GMM
- optionally fits an autoencoder if TensorFlow is installed
- prints scores for a specified 6D point

Run it as:

```bash
python3 scripts/probability_demo.py --point 1,2,3,4,5,6
```

To use a custom point:

```bash
python3 scripts/probability_demo.py --point 8,13,25,60,72,74
```

To skip the autoencoder step if TensorFlow is unavailable:

```bash
python3 scripts/probability_demo.py --skip-autoencoder
```
