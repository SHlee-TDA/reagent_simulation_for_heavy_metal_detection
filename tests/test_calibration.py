"""Effect-scale calibration: the data favour small effects (proposal 5.0)."""
import numpy as np
from rids.calibration import log_marginal


def test_effect_scale_small():
    r = log_marginal(n=600)
    assert r["experiments"] == 14
    s = np.array(r["s_grid"]); p = np.array(r["posterior_s"])
    assert p[s <= 0.3].sum() > 0.85          # s <= 0.3 with high probability
    assert r["log_bf_vs_null"][-1] < -2.5    # v2 prior (s = 1) clearly disfavoured
