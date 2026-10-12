"""Design utilities: Bayes-classifier balanced accuracy and greedy search
(proposal Sections 2.3, 4.1-4.2).  Works on any matrix of component means, so
stage 1 can call it with target responses Y directly.
"""
import numpy as np


def oracle_accuracy(mu, cls, cov, z):
    """Balanced accuracy of the Bayes classifier that knows the model.
    mu: (n_components, J) means; cls: class of each component (a class is a
    mixture over its concentration levels); cov: (J, J); z: (n, J) N(0,1) draws
    shared across designs (common random numbers).  Returns (BA, per-class acc)."""
    L = np.linalg.cholesky(cov)
    Li = np.linalg.inv(L)
    mw = mu @ Li.T
    samples = mw[:, None, :] + z[None, :, :mu.shape[1]]
    d2 = ((samples[:, :, None, :] - mw[None, None, :, :]) ** 2).sum(-1)
    logp = -0.5 * d2
    ncls = cls.max() + 1
    score = np.full(d2.shape[:2] + (ncls,), -np.inf)
    for k in range(ncls):
        sel = cls == k
        score[..., k] = np.logaddexp.reduce(logp[..., sel], axis=-1) - np.log(sel.sum())
    correct = (score.argmax(-1) == cls[:, None]).mean(1)
    per_class = np.array([correct[cls == k].mean() for k in range(ncls)])
    return float(per_class.mean()), per_class


def expected_utility(design, thetas, z, means_fn, cov_fn):
    J = len(design)
    cov = cov_fn(J)
    return float(np.mean([oracle_accuracy(*means_fn(design, th), cov, z)[0] for th in thetas]))


def greedy(library, thetas, z, means_fn, cov_fn, J=8):
    design = []
    for _ in range(J):
        best = max(library, key=lambda rc: expected_utility(design + [rc], thetas, z, means_fn, cov_fn))
        design.append(best)
    return design
