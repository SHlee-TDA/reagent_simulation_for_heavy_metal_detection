import numpy as np
from pfid import measurement as ms


def test_fit_lw_recovers_coefficient():
    rng = np.random.default_rng(0)
    t = np.arange(ms.REC_FRAMES)
    on = 71
    h = np.where(t < on, 0, ms.A0_PX + ms.K_WATER_PX * np.sqrt(np.clip(t - on, 0, None)))
    h = h + rng.normal(0, ms.FRONT_SD_PX, h.shape)
    f = ms.fit_lw(h)
    assert abs(f["b"] - ms.K_WATER_PX) < 0.05


def test_noise_cov_shape():
    C = ms.Noise().cov(8, 1, 2)
    assert C.shape == (8, 8) and np.all(np.linalg.eigvalsh(C) > 0)
