"""Effect-scale calibration on the 2026 screening data (proposal Section 5.0).

Data: data/derived/video_lw_coefficients.csv, one row per video (4 legs, same
condition): LW coefficient b of each leg.  DI-water experiments only.
Model per experiment: z_v = mu_day + s * y(cond_v; theta) + e_v,
e_v ~ N(0, sd_chip^2 + sd_leg^2/4); mu_day profiled out.  'As' -> As(V);
'Cr' -> Cr(III) or Cr(VI) with equal probability.
Returns log p(data | s) on a grid of s (Monte Carlo over the prior).
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import measurement as ms
from . import response_v2 as rv

ROOT = Path(__file__).resolve().parents[2]
REAG = {"Chi": "Chi", "Lys": "PLL", "Alg": "Alg", "Tan": "Tan", "Gal": "Gal"}
S_GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]


def load_di(path=ROOT / "data/derived/video_lw_coefficients.csv"):
    d = pd.read_csv(path)
    d["z"] = np.log(d[["b1", "b2", "b3", "b4"]]).mean(axis=1)
    di = d.exp.str.endswith("DI") | ~d.exp.str.contains("DI|PBS|NaCl|RSW")
    return d[di].reset_index(drop=True)


def effects(th, d, cr_species):
    y = np.zeros(len(d))
    for i, (m, c, r, rc) in enumerate(zip(d.metal, d.ppb, d.reagent, d.rconc)):
        metal = {"As": "As(V)", "Cr": cr_species}.get(m, m)
        recipe = ("none", 0) if rc == 0 else (REAG[r], rc)
        y[i] = rv.own_effect(recipe, th) + rv.response(recipe, metal if c > 0 else None, c, th)
    return y


def log_marginal(n=3000, seed=20261012, s_grid=S_GRID, sd_leg=ms.SD_LEG, sd_chip=ms.SD_CHIP):
    d = load_di()
    groups = [np.where(d.exp == e)[0] for e in d.exp.unique()]
    s2 = sd_chip ** 2 + sd_leg ** 2 / 4
    LL = np.zeros((n, 2, len(s_grid)))
    for i in range(n):
        th = rv.draw_theta(np.random.default_rng([seed, i]))
        for j, sp in enumerate(["Cr(III)", "Cr(VI)"]):
            y = effects(th, d, sp)
            for k, s in enumerate(s_grid):
                r = d.z.values - s * y
                LL[i, j, k] = sum(-0.5 * ((r[g] - r[g].mean()) ** 2).sum() / s2 for g in groups)
    ll = np.logaddexp(LL[:, 0], LL[:, 1]) - np.log(2)
    logml = np.logaddexp.reduce(ll, axis=0) - np.log(n)
    post = np.exp(logml - logml.max())
    return {"s_grid": list(s_grid), "log_bf_vs_null": (logml - logml[0]).tolist(),
            "posterior_s": (post / post.sum()).tolist(),
            "experiments": int(d.exp.nunique()), "videos": int(len(d))}
