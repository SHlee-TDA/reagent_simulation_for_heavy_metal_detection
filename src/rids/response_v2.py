"""Phenomenological response prior from simulator v2 (proposal Sections 2.2, 5.0).

y_j(m, c) = w_r(c_r) * e_{r,type(m)} * (1 + d_rm) * x / (x + X50_r) + a_m(c)
  w_r(c_r) = Wmax_r c_r / (c_r + C50_r)       reagent gain
  x = 1:1 complex from K_rm, c, c_r          (mass action)
Every coefficient carries a prior. This is the "named reagent" prior; stage 1
replaces it with property-space responses. Kept for design search and the
effect-scale calibration (calibration.py).
"""
import numpy as np

SPECIES = ["As(III)", "As(V)", "Cd", "Co", "Cr(III)", "Cr(VI)"]
PPB = {"As(III)": [1, 10, 100], "As(V)": [1, 10, 100], "Co": [1, 10, 100],
       "Cd": [5, 50, 500], "Cr(III)": [5, 50, 500], "Cr(VI)": [5, 50, 500]}
ATOMIC = {"As(III)": 74.92, "As(V)": 74.92, "Cd": 112.41, "Co": 58.93,
          "Cr(III)": 52.00, "Cr(VI)": 52.00}

REAGENTS = {   # g per mol of binding sites; status
    "none": (None, "in use"), "Chi": (161 / 0.85, "in use"), "PLL": (128.0, "in use"),
    "Alg": (198.0, "in use"), "Tan": (170.0, "in use"), "Gal": (170.0, "in use"),
    "Thiol": (300.0, "suggested"), "FeLa": (56.0, "suggested")}
# interaction type and mean log10 K (L/mol); None = no specific interaction
CHEM = {
    "Chi":   {"As(V)": ("anion", 2.5), "Cd": ("cation", 1.5), "Co": ("cation", 1.5),
              "Cr(III)": ("cation", 2.0), "Cr(VI)": ("redox", 3.5)},
    "PLL":   {"As(V)": ("anion", 3.0), "Cr(VI)": ("anion", 3.5)},
    "Alg":   {"Cd": ("cation", 4.0), "Co": ("cation", 3.0), "Cr(III)": ("cation", 4.5)},
    "Tan":   {"As(III)": ("neutral", 2.0), "As(V)": ("anion", 1.5), "Cd": ("cation", 3.0),
              "Co": ("cation", 3.0), "Cr(III)": ("cation", 4.5), "Cr(VI)": ("redox", 4.0)},
    "Gal":   {"As(III)": ("neutral", 2.0), "As(V)": ("anion", 1.5), "Cd": ("cation", 2.5),
              "Co": ("cation", 2.5), "Cr(III)": ("cation", 4.0), "Cr(VI)": ("redox", 4.0)},
    "Thiol": {"As(III)": ("neutral", 5.5), "As(V)": ("anion", 1.0), "Cd": ("cation", 5.0),
              "Co": ("cation", 3.0), "Cr(III)": ("cation", 1.0), "Cr(VI)": ("redox", 4.0)},
    "FeLa":  {"As(III)": ("neutral", 3.5), "As(V)": ("anion", 5.0), "Cr(VI)": ("anion", 3.0)},
}
GAIN_SD = {"Chi": 0.10, "PLL": 0.10, "Alg": 0.10, "Tan": 0.10, "Gal": 0.05,
           "Thiol": 0.10, "FeLa": 0.10}
LOGK_SD = 1.0
CONC_GRID = [1, 10, 100, 1000, 10000, 100000]   # ppb, before mixing
TYPES = ("anion", "cation", "redox", "neutral")


def recipe_list(include_suggested=True):
    out = [("none", 0)]
    for r, (_, status) in REAGENTS.items():
        if r == "none" or (status == "suggested" and not include_suggested):
            continue
        out += [(r, c) for c in CONC_GRID]
    return out


def draw_theta(rng, species=SPECIES, scale=1.0, scaled=("Chi", "PLL", "Alg", "Tan", "Gal")):
    """One prior draw. `scale` multiplies the gains of `scaled` reagents and the
    metal-only terms (effect-scale calibration, calibration.py)."""
    th = {"metal_only": {m: scale * rng.normal(0, 0.01) for m in species}}
    for r in CHEM:
        s = scale if r in scaled else 1.0
        th[r] = {"Wmax": s * rng.normal(0, GAIN_SD[r]), "logC50": rng.uniform(2, 5),
                 "logX50": rng.uniform(-9, -5),
                 "e": {t: rng.normal(0, 1) for t in TYPES}, "logK": {}, "d": {}}
        for m in species:
            if m in CHEM[r]:
                th[r]["logK"][m] = rng.normal(CHEM[r][m][1], LOGK_SD)
                th[r]["d"][m] = rng.normal(0, 0.3)
    return th


def complex_conc(a, b, K):
    if a <= 0 or b <= 0:
        return 0.0
    s = a + b + 1.0 / K
    return 2 * a * b / (s + np.sqrt(max(s * s - 4 * a * b, 0.0)))


def own_effect(recipe, th):
    r, c_r = recipe
    if r == "none" or c_r == 0:
        return 0.0
    return th[r]["Wmax"] * c_r / (c_r + 10 ** th[r]["logC50"])


def response(recipe, metal, ppb, th):
    """y for one leg relative to the zero control of the same recipe."""
    if metal is None or ppb == 0:
        return 0.0
    y = th["metal_only"][metal] * ppb / max(PPB[metal])
    r, c_r = recipe
    if r == "none" or metal not in th[r]["logK"]:
        return y
    p = th[r]
    a = ppb * 1e-6 / ATOMIC[metal] / 2
    b = c_r * 1e-6 / REAGENTS[r][0] / 2
    x = complex_conc(a, b, 10 ** p["logK"][metal])
    typ = CHEM[r][metal][0]
    return y + own_effect(recipe, th) * p["e"][typ] * (1 + p["d"][metal]) * x / (x + 10 ** p["logX50"])


def means(design, th, species=SPECIES):
    """Component means (n_components, J) and class index (0 = not added)."""
    rows, cls = [np.zeros(len(design))], [0]
    for i, m in enumerate(species, 1):
        for c in PPB[m]:
            rows.append([response(rc, m, c, th) for rc in design])
            cls.append(i)
    return np.array(rows), np.array(cls)
