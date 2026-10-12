"""Feasibility filter F (strategy doc, Section 6.3). Thresholds come from Stage1Config.

A candidate is a dict with (at least) keys:
  name, catalog (bool), price_per_g (float or None), ghs (list of H-codes),
  solubility_g_per_L (float or None), c_needed_g_per_L (float), ph_range ([lo, hi])
"""
from ..config import Stage1Config


def reasons_to_exclude(cand: dict, cfg: Stage1Config):
    out = []
    if cfg.require_catalog and not cand.get("catalog", False):
        out.append("not in a catalog")
    p = cand.get("price_per_g")
    if cfg.price_max_per_g is not None and p is not None and p > cfg.price_max_per_g:
        out.append(f"price {p} > {cfg.price_max_per_g} per g")
    bad = sorted(set(cand.get("ghs", [])) & set(cfg.ghs_exclude))
    if bad:
        out.append("hazard " + ",".join(bad))
    sol, need = cand.get("solubility_g_per_L"), cand.get("c_needed_g_per_L")
    if sol is not None and need is not None and need > sol:
        out.append("not soluble at the needed concentration")
    lo, hi = cand.get("ph_range", [0, 14])
    if hi < cfg.ph_window[0] or lo > cfg.ph_window[1]:
        out.append("pH range outside the window")
    return out


def feasible(cands, cfg):
    return [c for c in cands if not reasons_to_exclude(c, cfg)]
