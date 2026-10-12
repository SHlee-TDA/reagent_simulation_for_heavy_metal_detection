"""Choices that are conventions, not measurements, live here as parameters.

Load a run configuration with `load_config(path_or_json)`; every field of
Stage1Config can be overridden. Shipped configs: configs/*.json.
"""
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import measurement as ms

ATOMIC = {"As": 74.92, "Cd": 112.41, "Cr": 52.00, "Co": 58.93}

# Anchor concentrations in ug/L (= ppb). None = the standard lists no value.
STANDARDS = {
    # values listed as surface-water limits in jiyou's 2026-09-02 slides
    "jiyou_surface": {"As": 10, "Cd": 50, "Cr": 50, "Co": None},
    # Korean drinking-water standard (mokpo.go.kr comparison table)
    "KR_drinking": {"As": 10, "Cd": 5, "Cr": 50, "Co": None},
    # WHO GDWQ 4th ed. (Cr = total chromium)
    "WHO": {"As": 10, "Cd": 3, "Cr": 50, "Co": None},
}


@dataclass
class Stage1Config:
    name: str = "default"
    # anchors
    standard: str = "jiyou_surface"
    c_star_override: dict = field(default_factory=lambda: {"Co": 10})   # ug/L
    mix_ratio: float = 0.5               # sample:reagent 1:1
    bound_fraction: float = 1.0          # f, fraction of metal in the complex
    # task
    alpha: float = 0.9                   # target pairwise accuracy
    rho: float = 2.0                     # level task: c <= c*/rho vs c >= rho c*
    # protocol and noise
    J: int = 8
    R: int = 1
    n_ctrl: int = 2
    sd_leg: float = ms.SD_LEG
    sd_chip: float = ms.SD_CHIP
    # stage-2 feasibility filter (recorded here, applied in stage2)
    price_max_per_g: float | None = None
    ghs_exclude: list = field(default_factory=lambda: [
        "H300", "H310", "H330", "H340", "H350", "H360"])
    require_catalog: bool = True
    ph_window: list = field(default_factory=lambda: [5.0, 8.0])
    # stage-1b channel constants
    gamma0: float = 0.072                # N/m, water
    Gamma_inf_range: list = field(default_factory=lambda: [2e-6, 4e-6])   # mol/m^2

    def c_star(self):
        base = dict(STANDARDS.get(self.standard, {}))
        base.update(self.c_star_override)
        return base

    def x_star(self):
        """Complex concentration (mol/L) at the anchor, after mixing."""
        return {m: (None if c is None else
                    c * 1e-6 / ATOMIC[m] * self.mix_ratio * self.bound_fraction)
                for m, c in self.c_star().items()}

    def noise(self):
        return ms.Noise(self.sd_leg, self.sd_chip)

    def to_dict(self):
        return asdict(self)


def load_config(src=None):
    cfg = Stage1Config()
    if src:
        p = Path(src)
        d = json.loads(p.read_text()) if p.exists() else json.loads(src)
        for k, v in d.items():
            if not hasattr(cfg, k):
                raise KeyError(f"unknown config field: {k}")
            setattr(cfg, k, v)
    return cfg
