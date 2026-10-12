# pfid — property-space inverse design for paper-wicking heavy-metal classification

Paper chips classify a sample from how fast the sample–reagent mixture wicks
(Lucas–Washburn flow coefficient k). This project finds reagent recipes that make
heavy metals (As(III), As(V), Cd, Co, Cr(III), Cr(VI)) classifiable at regulatory
concentrations, in two stages:

1. **Stage 1:** design target responses in property space (surface tension,
   contact angle, viscosity) within physical constraints.
2. **Stage 2:** find real compounds, concentrations and pH that realize them,
   excluding unavailable, expensive or hazardous options.

Plan and notation: see `docs/README.md` and `CLAUDE.md`.

## Quick start

```bash
pip install -e .[dev]
pytest -q
python scripts/run_stage1a.py configs/jiyou_surface.json
```

## Layout

```
configs/        run configurations (anchors and other conventions as parameters)
data/raw/       provided data (read only)
data/derived/   our summaries of the 2026 screening videos
docs/           calibration note and links to the project documents
references/     slides, chip geometry, lab processing notebook (see references/README.md)
runs/           one folder per run: config, results, git hash
scripts/        entry points
src/pfid/       measurement, config, stage1a, stage1b, stage2, design, calibration
tests/          reproduce the numbers quoted in the documents
```

Private repository: contains unpublished lab data.
