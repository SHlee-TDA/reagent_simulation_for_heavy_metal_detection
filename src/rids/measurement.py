"""Measurement model, calibrated on jiyou's 2026 screening videos.

Source: 42 experiments, 1,039 videos, 4,156 legs (docs/calibration_2026-10-12.md).
The recording protocol is fixed (30 fps, 60 s); only the analysis is ours.

Flow profile of leg j:  h_j(t) = a_j + k_j sqrt(t),  t = frames after tip contact,
fitted on t >= FIT_FROM_FR.  Observable:  y_j = log k_j(m, c) - log k_j(0, 0).
"""
from dataclasses import dataclass

import numpy as np

# --- recording and geometry ---------------------------------------------------
FPS = 30                    # notebook output: 29.99 fps
REC_FRAMES = 1800           # 60 s, fixed
ONSET_FR = 71               # median frame of tip contact (front >= 20 px)
N_POST_FR = REC_FRAMES - ONSET_FR
PX_PER_MM = 13.3            # finger 24 mm ~ 318 px; width 6 mm ~ 78 px; +-5 % between sessions
FINGER_MM = 24.0            # analysis stops at the end of the finger (collection pad excluded)
ROI_ROWS = (645, 974)       # lab notebook ROI (329 px), vertical lanes, 142 px apart

# --- flow -----------------------------------------------------------------------
K_WATER_PX = 4.83           # px / sqrt(frame), median LW coefficient (1.99 mm / sqrt(s))
A0_PX, A0_SD_PX = 32.0, 12.0
FIT_FROM_FR = 30            # fit from 1 s after contact
FRONT_SD_PX = 1.5           # LW-fit residual (median 1.46 px)

# --- variability of log k (full-curve fit, same-condition replicates) -----------
SD_LEG, SD_CHIP, SD_DAY = 0.041, 0.036, 0.050
LEGACY_SD = (0.09, 0.08, 0.07)   # 15-frame windowed slopes (pre-calibration)


def fit_lw(h, onset_threshold=20, fit_from=FIT_FROM_FR):
    """Fit h = a + b sqrt(t - onset) to one leg's raw flow profile (px per frame).
    Returns dict(onset, a, b, resid_sd)."""
    h = np.asarray(h, float)
    on = int(np.argmax(h >= onset_threshold))
    t = np.arange(len(h)) - on
    sel = t >= fit_from
    x = np.sqrt(t[sel])
    X = np.c_[np.ones_like(x), x]
    coef, *_ = np.linalg.lstsq(X, h[sel], rcond=None)
    r = h[sel] - X @ coef
    return {"onset": on, "a": float(coef[0]), "b": float(coef[1]), "resid_sd": float(r.std())}


@dataclass
class Noise:
    sd_leg: float = SD_LEG
    sd_chip: float = SD_CHIP
    legs_per_chip: int = 4

    def cov(self, J=8, R=1, n_ctrl=2):
        """Covariance of y: sample averaged over R runs minus the mean of n_ctrl
        same-day zero controls. Legs 0-3 = chip A, 4-7 = chip B (day effect cancels)."""
        chip = np.arange(J) // self.legs_per_chip
        run = self.sd_leg ** 2 * np.eye(J) + self.sd_chip ** 2 * (chip[:, None] == chip[None, :])
        return run / R + run / n_ctrl
