"""Probability estimates for new 6D points using PCA, GMM, and Autoencoder models."""

import numpy as np


def fit_pca(H, k=2):
    """Fit PCA and estimate residual noise variance for later probability scoring."""
    from sklearn.decomposition import PCA

    pca = PCA(n_components=k, svd_solver='full')
    pca.fit(H)
    if hasattr(pca, 'noise_variance_') and pca.noise_variance_ is not None:
        noise_var = float(np.mean(pca.noise_variance_))
    else:
        X_rec = pca.inverse_transform(pca.transform(H))
        noise_var = float(np.mean(np.sum((H - X_rec) ** 2, axis=1)))
    return pca, noise_var


def pca_probability(p, pca, noise_var):
    """Estimate a pseudo-probability for point p under the PCA model.

    This uses the reconstruction error from the PCA projection and
    converts it into a score with a Gaussian noise assumption.
    """
    x = np.asarray(p, dtype=float).reshape(1, -1)
    z = pca.transform(x)
    x_rec = pca.inverse_transform(z)
    error_sq = float(np.sum((x - x_rec) ** 2))
    if noise_var <= 0:
        noise_var = 1e-8
    score = float(np.exp(-0.5 * error_sq / noise_var))
    return score


def gmm_probability(p, gmm):
    """Return a density score for point p from a fitted GaussianMixture."""
    x = np.asarray(p, dtype=float).reshape(1, -1)
    log_density = gmm.score_samples(x)[0]
    density = float(np.exp(log_density))
    return density


def gmm_responsibilities(p, gmm):
    """Return the per-component mixture responsibility of point p."""
    x = np.asarray(p, dtype=float).reshape(1, -1)
    return gmm.predict_proba(x)[0]


def fit_autoencoder(H, latent_dim=2, epochs=200, batch_size=32, verbose=0):
    """Fit an autoencoder and return encoder/decoder plus training reconstruction MSE."""
    import tensorflow as tf
    from tensorflow.keras import layers, models, optimizers

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

    recon = ae.predict(X)
    mse = float(np.mean(np.sum((X - recon) ** 2, axis=1)))
    return {'autoencoder': ae, 'encoder': encoder, 'decoder': decoder, 'reconstruction_mse': mse}


def autoencoder_probability(p, encoder, decoder, noise_var=None):
    """Estimate a pseudo-probability for point p based on autoencoder reconstruction error."""
    x = np.asarray(p, dtype='float32').reshape(1, -1)
    z = encoder.predict(x)
    x_rec = decoder.predict(z)
    error_sq = float(np.sum((x - x_rec) ** 2))
    if noise_var is None or noise_var <= 0:
        noise_var = 1.0
    score = float(np.exp(-0.5 * error_sq / noise_var))
    return score


if __name__ == '__main__':
    raise SystemExit('This module provides helper functions and is not meant to be executed directly.')
