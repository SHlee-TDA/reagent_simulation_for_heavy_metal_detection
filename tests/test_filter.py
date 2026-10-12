from pfid.config import Stage1Config
from pfid.stage2.filter import reasons_to_exclude


def test_filter_excludes_hazard_and_price():
    cfg = Stage1Config(price_max_per_g=50)
    c = {"name": "x", "catalog": True, "price_per_g": 80, "ghs": ["H350"], "ph_range": [6, 7]}
    r = reasons_to_exclude(c, cfg)
    assert any("price" in s for s in r) and any("H350" in s for s in r)
