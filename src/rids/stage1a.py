"""Stage 1(a): target response in observation space (strategy doc, Section 4).

Implemented: required size delta_min and required amplification A* at the
regulatory anchors.  To do (P1): the target-response problem

    Y* = argmin_{Y in A_Y} max_{j,m} |Y_jm| / x*_m   s.t.  BA_s(Y; Sigma) >= alpha_s

for each stage s (detection, speciation, level), using design.oracle_accuracy.
"""
import numpy as np
from scipy.stats import norm

from .config import Stage1Config


def sign_patterns(J):
    return {"same sign": np.ones(J),
            "mixed sign": np.array([(-1) ** j for j in range(J)], float)}


def delta_min(cfg: Stage1Config, u):
    """Smallest per-leg |y| that separates two classes with accuracy alpha when
    their difference has sign pattern u (Gaussian, Mahalanobis)."""
    C = cfg.noise().cov(cfg.J, cfg.R, cfg.n_ctrl)
    return float(2 * norm.ppf(cfg.alpha) / np.sqrt(u @ np.linalg.solve(C, u)))


def amplification_table(cfg: Stage1Config):
    """delta_min and A*_m = 2 delta_min / x*_m (per mol/L of complex)."""
    xs = cfg.x_star()
    rows = []
    for name, u in sign_patterns(cfg.J).items():
        d = delta_min(cfg, u)
        rows.append({"pattern": name, "delta_min": d,
                     "delta_level": d / (cfg.rho - 1 / cfg.rho),
                     "A_star": {m: (None if x is None else 2 * d / x) for m, x in xs.items()}})
    return {"c_star_ugL": cfg.c_star(),
            "x_star_nM": {m: (None if x is None else x * 1e9) for m, x in xs.items()},
            "rows": rows}
