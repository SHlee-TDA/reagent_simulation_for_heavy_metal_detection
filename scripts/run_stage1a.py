"""Stage 1(a) run: required size and amplification for one config.
Usage: python scripts/run_stage1a.py configs/jiyou_surface.json
Writes runs/<YYYY-MM-DD>_stage1a_<name>/{config.json, results.json, meta.json}."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from pfid.config import load_config
from pfid.stage1a import amplification_table

ROOT = Path(__file__).resolve().parents[1]


def git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "uncommitted"


def main(src):
    cfg = load_config(src)
    res = amplification_table(cfg)
    out = ROOT / "runs" / f"{dt.date.today()}_stage1a_{cfg.name}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(cfg.to_dict(), indent=1))
    (out / "results.json").write_text(json.dumps(res, indent=1))
    (out / "meta.json").write_text(json.dumps({"git": git_hash(), "argv": sys.argv}, indent=1))
    print(f"[{cfg.name}] c* (ug/L) {res['c_star_ugL']}  x* (nM) "
          + str({m: (None if v is None else round(v, 1)) for m, v in res['x_star_nM'].items()}))
    for r in res["rows"]:
        A = {m: (None if v is None else f"{v:.2g}") for m, v in r["A_star"].items()}
        print(f"  {r['pattern']:10s} delta_min {r['delta_min']:.3f}  level {r['delta_level']:.3f}  A* {A}")
    print("->", out.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
