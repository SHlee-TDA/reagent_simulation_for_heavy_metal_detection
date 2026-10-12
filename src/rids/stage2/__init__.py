"""Stage 2: chemical realization (strategy doc, Section 6).

To do (P3):
  candidates.py  candidate space Q, one record per (compound, mechanism class)
  forward.py     F_q: (c_q, pH; m, c) -> (gamma, theta, eta), parameters psi_q with priors
  inverse.py     (a) shortlist by distance to Y*_j, (b) design search over F^J
Implemented: the feasibility filter F (filter.py).
"""
