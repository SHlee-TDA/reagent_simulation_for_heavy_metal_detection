"""Reproduce the strategy-doc Section 4 numbers (KR drinking-water anchors)."""
import pytest
from pfid.config import load_config
from pfid.stage1a import amplification_table


def test_kr_drinking_table():
    res = amplification_table(load_config('{"standard": "KR_drinking"}'))
    rows = {r["pattern"]: r for r in res["rows"]}
    assert rows["same sign"]["delta_min"] == pytest.approx(0.092, abs=0.001)
    assert rows["mixed sign"]["delta_min"] == pytest.approx(0.0455, abs=0.001)
    A = rows["mixed sign"]["A_star"]
    assert A["As"] == pytest.approx(1.4e6, rel=0.05)
    assert A["Cd"] == pytest.approx(4.1e6, rel=0.05)
    assert A["Cr"] == pytest.approx(1.9e5, rel=0.05)
    assert res["x_star_nM"]["Cd"] == pytest.approx(22.2, abs=0.2)


def test_jiyou_cd_is_tenfold_easier():
    kr = amplification_table(load_config('{"standard": "KR_drinking"}'))["rows"][1]["A_star"]["Cd"]
    ji = amplification_table(load_config('{"standard": "jiyou_surface"}'))["rows"][1]["A_star"]["Cd"]
    assert kr / ji == pytest.approx(10, rel=1e-6)
