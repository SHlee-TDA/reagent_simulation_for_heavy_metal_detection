"""Manifest-pinned organization and preservation of archived legacy AIC data."""
from pathlib import Path
import json
import re
import tempfile

import numpy as np
import pandas as pd

from ..core.artifacts import digest, dump, safe_path
from ..core.contracts import ATOL, COLUMNS, KEY, SCHEMA_VERSION, ContractError, validate_aic
from .features import assert_control_parity


def inventory(root, source_dir="AIC_Data"):
    """Register known legacy naming convention; do not recursively merge outputs."""
    root = Path(root).resolve()
    sources, snapshots = [], []
    for path in sorted(safe_path(root, source_dir).rglob("*.csv")):
        name = path.name
        entry = {"path": path.relative_to(root).as_posix(), "sha256": digest(path)}
        if re.fullmatch(r"\d{4}_\d{2}_\d{2}_.+_aic\.csv", name):
            d = validate_aic(pd.read_csv(path))
            entry.update(source_id="legacy-" + path.stem, rows=len(d),
                         provenance_status="unverified", sample_id=None, site_id=None,
                         concentration_unit=None, drive_file_id=None)
            sources.append(entry)
        elif "combined" in name.lower():
            d = pd.read_csv(path)
            if "SourceFile" not in d or d.SourceFile.isna().any():
                raise ContractError(f"Snapshot lacks source lineage: {name}")
            entry.update(snapshot_id=path.stem, rows=len(d), sources=sorted(d.SourceFile.unique()))
            snapshots.append(entry)
        else:
            raise ContractError(f"Unrecognized CSV; register its role explicitly: {path}")
    if not sources:
        raise ContractError("No individual sources found")
    if len({s["source_id"] for s in sources}) != len(sources):
        raise ContractError("Source filename collision; assign distinct source IDs")
    return {"schema_version": SCHEMA_VERSION, "adapter": "legacy_aic_v1",
            "sources": sources, "snapshots": snapshots}


def load_sources(root, manifest):
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("adapter") != "legacy_aic_v1":
        raise ContractError("Unsupported manifest version or adapter")
    result = {}
    seen_paths, seen_hashes = set(), set()
    for entry in manifest["sources"]:
        sid = entry["source_id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", sid):
            raise ContractError("Unsafe source ID")
        path = safe_path(root, entry["path"])
        if sid in result or path in seen_paths:
            raise ContractError("Duplicate source entry")
        seen_paths.add(path)
        if digest(path) != entry["sha256"]:
            raise ContractError(f"Source hash changed: {entry['path']}")
        if entry["sha256"] in seen_hashes:
            raise ContractError("Duplicate source content; review before registration")
        seen_hashes.add(entry["sha256"])
        d = validate_aic(pd.read_csv(path))
        if len(d) != entry["rows"]:
            raise ContractError("Source row count changed")
        assert_control_parity(d)
        result[sid] = (entry, d)
    if not result:
        raise ContractError("Empty source manifest")
    return result


def missing_windows(d):
    """Report absent measurements, not just NaN cells. Never infer their cause."""
    expected = set(range(15, 301, 15))
    records = []
    for combo in sorted(d.Combo.unique()):
        part = d[d.Combo == combo]
        for channel in range(8):
            missing = sorted(expected-set(part.loc[part.Channel == channel, "WindowEdge"]))
            if missing:
                records.append({"combo": combo, "channel": channel, "missing_windows": missing,
                                "reason": "unverified", "status": "review_required"})
    return records


def reconcile_snapshot(root, snapshot, sources):
    path = safe_path(root, snapshot["path"])
    if digest(path) != snapshot["sha256"]:
        raise ContractError("Reference snapshot hash changed")
    reference = pd.read_csv(path)
    if set(reference.columns) != set(COLUMNS+["SourceFile"]):
        raise ContractError("Unexpected snapshot columns")
    if len(reference) != snapshot["rows"] or sorted(reference.SourceFile.unique()) != snapshot["sources"]:
        raise ContractError("Reference snapshot membership changed")
    by_name = {Path(e["path"]).name: d for e, d in sources.values()}
    if len(by_name) != len(sources):
        raise ContractError("Ambiguous source filenames")
    try:
        rebuilt = pd.concat([by_name[s].assign(SourceFile=s) for s in snapshot["sources"]], ignore_index=True)
    except KeyError as exc:
        raise ContractError(f"Missing snapshot source: {exc}") from exc
    key = ["SourceFile"]+KEY
    try:
        paired = reference.merge(rebuilt, on=key, suffixes=("_old", "_new"), how="outer", indicator=True, validate="one_to_one")
    except pd.errors.MergeError as exc:
        raise ContractError("Duplicate snapshot measurement") from exc
    if not (paired._merge == "both").all():
        raise ContractError("Snapshot row membership differs")
    errors = {}
    for col in COLUMNS:
        if col in KEY:
            continue
        a, b = paired[col+"_old"], paired[col+"_new"]
        if pd.api.types.is_numeric_dtype(a):
            if not np.allclose(a, b, atol=ATOL, rtol=0):
                raise ContractError(f"Snapshot values differ: {col}")
            errors[col] = float((a-b).abs().max())
        elif not a.eq(b).all():
            raise ContractError(f"Snapshot labels differ: {col}")
    return rebuilt, {"snapshot_id": snapshot["snapshot_id"], "rows": len(rebuilt),
                     "status": "passed", "max_absolute_errors": errors}


def build_release(root, manifest, release_id):
    """Write a new immutable legacy release only after all validation succeeds."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", release_id):
        raise ContractError("Invalid release ID")
    root = Path(root).resolve()
    destination = root / "data" / "releases" / release_id
    if destination.exists():
        raise ContractError("Release already exists; use a new ID or verify the existing release")
    sources = load_sources(root, manifest)
    frames, qc = [], []
    for sid, (entry, d) in sources.items():
        q = d.copy()
        q.insert(0, "source_id", sid)
        q.insert(1, "source_row", np.arange(1, len(q)+1))
        q["source_sha256"] = entry["sha256"]
        q["feature_definition_id"] = "legacy_sqrt_frame_slope_v1"
        q["provenance_status"] = "unverified"
        # Biological IDs remain unset until reviewed; channel positions are NOT samples.
        for c in ["sample_id", "site_id", "concentration_unit"]:
            q[c] = None
        frames.append(q)
        qc.append({"source_id": sid, "rows": len(d), "control_parity": assert_control_parity(d),
                   "incomplete_profiles": missing_windows(d)})
    snapshots = [reconcile_snapshot(root, s, sources) for s in manifest["snapshots"]]
    all_data = pd.concat(frames, ignore_index=True)
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    # A failed build leaves no apparently valid release.
    with tempfile.TemporaryDirectory(prefix=".staging-", dir=parent) as tmp:
        staging = Path(tmp) / "release"
        staging.mkdir()
        all_data.to_csv(staging / "measurements.csv", index=False)
        (staging / "snapshots").mkdir()
        for rebuilt, check in snapshots:
            sid = check["snapshot_id"]
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", sid):
                raise ContractError("Unsafe snapshot ID")
            rebuilt.to_csv(staging / "snapshots" / (sid+".csv"), index=False)
        dump(staging / "source_manifest.json", manifest)
        report = {"release_id": release_id, "schema_version": SCHEMA_VERSION,
                  "processor_version": "0.1.0",
                  "processor_sha256": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                  "runtime": {"numpy": np.__version__, "pandas": pd.__version__},
                  "status": "legacy_unverified", "scientific_validation_ready": False,
                  "rows": len(all_data), "sources": len(sources),
                  "note": "Numerical preservation passed. Sample/site/units and acquisition provenance require review.",
                  "sources_qc": qc, "snapshot_parity": [check for _, check in snapshots]}
        dump(staging / "validation.json", report)
        hashes = {p.relative_to(staging).as_posix(): digest(p) for p in sorted(staging.rglob("*")) if p.is_file()}
        dump(staging / "checksums.json", hashes)
        staging.rename(destination)
    return destination


def verify_release(path):
    path = Path(path)
    hashes = json.loads((path / "checksums.json").read_text(encoding="utf-8"))
    actual = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file() and p.name != "checksums.json"}
    if actual != set(hashes):
        raise ContractError("Release file inventory changed")
    for name, expected in hashes.items():
        if digest(safe_path(path, name)) != expected:
            raise ContractError(f"Release checksum mismatch: {name}")
    return json.loads((path / "validation.json").read_text(encoding="utf-8"))
