# CLAUDE.md — pfid

Read this first. It records what has been agreed, so a new session can start
without the earlier conversation.

## People and roles

- **S. Lee** (project lead, mathematics/ML, POSTECH GSAI). Owns the simulation and
  the mathematical formulation. Not a chemist: chemistry enters through models and
  data, and is checked with jiyou.
- **jiyou** (W. Areekul, chemistry, runs the experiments). Always refer to them as "jiyou".
  Chooses reagents and runs SALSA-style screening. Keep requests to jiyou small.

Reply to S. Lee in Korean unless asked otherwise. Code, comments and this file are in English.

## Goal

Find reagent recipes that make heavy metals classifiable from paper-wicking flow,
and do it as a **two-stage inverse design** (strategy doc, Sections 3-6):

1. **Stage 1 (mathematics).** Find *pseudo-recipes* in property space: response
   maps (metal, concentration) -> (gamma, theta, eta) that make the observed flow
   coefficients classifiable, inside what nature allows (mass action, Gibbs
   adsorption, Young, polymer viscosity, metal-exchange symmetry and its breaking).
   - 1a: target response Y* in observation space (required size, amplification).
   - 1b: admissible set A_P and the pseudo-recipe P* on the fibre phi^{-1}(Y*).
2. **Stage 2 (chemistry).** Find real (compound, concentration, pH) that realize P*,
   with forward property models and a feasibility filter (available, affordable,
   safe, soluble, pH-compatible). Rank candidates for jiyou's screening.

The library-based search (choose among named reagents) is exhausted: the five
reagents tested in 2026 show no effect beyond chip variability (Bayes factor
about 1:170 against the v2 prior effect sizes). That is why we design in property space.

## Agreed terminology and notation

Follow the proposal (Sec. 2.0-2.2, 3) and the strategy doc (Sec. 2). Do not rename.

| Term / symbol | Meaning |
| --- | --- |
| reagent | molecule mixed 1:1 with the sample (SALSA: BIM) |
| recipe r_j | reagent + reagent concentration + solvent/pH |
| design d | recipes on one sample's legs: 2 chips x 4 legs, J = 8 |
| leg, chip, day | one finger; one paper chip (4 legs); preparation day |
| matrix | water background (DI, PBS, NaCl, river/sea water); we model DI only |
| flow profile h_j(t) | front position (px) vs frame |
| flow coefficient k_j = sqrt(D_j) | h = a + k sqrt(t);  D_j ∝ r_eff gamma_j cos(theta_j) / eta_j |
| y_j | log k_j(m, c) - log k_j(0, 0), same-day zero control |
| not added | sample without metal; its own class |
| R = S·M | response = gain S (recipes x mechanisms) · engagement M (mechanisms x metals) |
| fingerprint v_m, ṽ_m | metal m's response vector over the design; ṽ whitened |
| separability Δ_mm', c_min | class distance; gain x selectivity (Propositions 1-3) |
| mechanism index **ν** | proposal's k; renamed to avoid clash with flow coefficient k |
| angle **∠(v_m, v_m')** | proposal's θ_mm'; renamed to avoid clash with contact angle θ |
| p = (gamma, theta, eta) | surface tension, contact angle, viscosity (eta, not mu) |
| phi(p) | 0.5 log(gamma cos theta / eta), the observation map |
| pseudo-recipe P_j | (m, c) -> p_j(m, c) for leg j |
| A_P, A_Y | admissible sets in property / observation space |
| c⋆_m, x⋆_m | anchor concentration (regulatory), complex concentration after mixing |
| delta_min, A⋆ | required per-leg |y|; required amplification (per mol/L of complex) |
| Q, F | stage-2 candidate space and feasibility filter |
| Proposition 4 | fibre invariance of phi (strategy doc 3) |
| Proposition 5 | metal-exchange symmetry within a charge class (strategy doc 5.3) |

## Decisions already made

- **Recording is fixed:** 30 fps, 60 s (~1,800 frames). Never propose changing it.
  Only analysis, recipe choice and protocol (replicates, controls, leg assignment) are ours.
- **Analysis window:** the finger only (24 mm); the collection pad is excluded.
  In 60 s the front reaches ~17 mm (never 24 mm); use the whole profile after contact.
- **Feature:** one LW coefficient fitted to the whole profile (t >= 1 s after contact),
  not the legacy 15-frame windowed slopes.
- **Chip QC is out of scope** for S. Lee; use measured noise, do not propose QC work.
- **No color information.**
- **Species:** As(III), As(V), Cd, Co, Cr(III), Cr(VI) + not added. jiyou's grouping =
  label pooling (As = III or V, Cr = III or VI), not mixing samples.
  Staged task: detection -> speciation -> level vs anchor.
- **Anchors are parameters** (`pfid.config.Stage1Config`). Run order agreed on 2026-10-12:
  **jiyou_surface first** (As 10, Cd 50, Cr 50 ug/L; Co 10 by choice), report, then
  KR_drinking (Cd 5) and WHO (Cd 3).
- Defaults: alpha = 0.9, rho = 2, R = 1, n_ctrl = 2, mix 1:1, bound fraction 1.

## Calibrated measurement (2026-10-12, docs/calibration_2026-10-12.md)

13.3 px/mm; onset ~ frame 71; b = 4.83 px/sqrt(frame) (4.28-5.42); fit residual 1.5 px;
noise in log k: leg 4.1 %, chip 3.6 %, day 5.0 % (legacy windowed slopes: 9/8/7 %).
Pooled ANOVA over 41 experiments: F = 0.72 (no condition effect in any of 7 features).

## Current state and next step

- P0 done (calibration). Stage-1a amplification table implemented (`pfid.stage1a`).
- **Next: P1** with `configs/jiyou_surface.json`: solve the target-response problem
  (strategy doc 4.4) per stage, report, then rerun with the other anchor configs.
- Then P2 (stage 1b bounds, falsification test 1), P3 (stage 2), P4 (screening loop).

## Repository conventions

- `src/pfid/`: library. `scripts/`: entry points. `configs/`: run configs (JSON).
- Every run writes `runs/<date>_<stage>_<config>/` with config.json, results.json,
  meta.json (git hash). Never overwrite a past run.
- `tests/` must keep reproducing the numbers quoted in the docs; update tests and
  docs together.
- Data: `data/raw/` as provided (read only), `data/derived/` our summaries.
  Raw videos stay in the lab Drive; never commit videos.
- Install: `pip install -e .[dev]`; test: `pytest -q`;
  run: `python scripts/run_stage1a.py configs/jiyou_surface.json`.

## Documents

See `docs/README.md` (strategy doc = current plan; proposal = terminology and theory).
