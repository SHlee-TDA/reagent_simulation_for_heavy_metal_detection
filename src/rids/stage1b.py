"""Stage 1(b): admissible set A_P in property space (strategy doc, Section 5).

Implemented: per-channel amplification bounds (Henry regime) and the
speciation classes / symmetry-breaking axes.  To do (P2): bounds over literature
ranges, the pseudo-recipe problem

    P*_j = argmin_{P in A_P ∩ phi^{-1}(Y*_j)}  sum_i A_i(P) / A_i^max,

and falsification test 1 (reproduce the null effect of the five tested reagents).
"""
import numpy as np

R_GAS, T_K = 8.314, 298.15


def phi(gamma, theta, eta):
    """Observation map: 0.5 * log(gamma cos(theta) / eta)."""
    return 0.5 * np.log(gamma * np.cos(theta) / eta)


def A_gamma(dK_L, Gamma_inf=3e-6, gamma0=0.072):
    """Surface tension (Szyszkowski, Henry regime): |dlog gamma| per mol/L of complex."""
    return R_GAS * T_K * Gamma_inf / gamma0 * dK_L


def A_eta(n_ch, eta_sp, a=0.7, eps=1.0):
    """Viscosity via inter-chain bridging of dilute chains (Mark-Houwink exponent a,
    bridging efficiency eps, chain molarity n_ch): |dlog eta| per mol/L of bridges."""
    return 2 * a * eps * eta_sp / (1 + eta_sp) / n_ch


def A_theta(dK_s, Gamma_sl=3e-6, gamma0=0.072, theta0=np.deg2rad(30)):
    """Contact angle via adsorption at the solid-liquid interface (Young)."""
    return R_GAS * T_K * Gamma_sl / (gamma0 * np.cos(theta0)) * dK_s


# Speciation near neutral pH after mixing, and the axes that break the
# metal-exchange symmetry (Proposition 5).
CHARGE_CLASS = {"Cd": "cation", "Co": "cation", "Cr(III)": "cation",
                "As(V)": "oxyanion", "Cr(VI)": "oxyanion", "As(III)": "neutral"}
SYMMETRY_AXES = {
    "charge": "cation / oxyanion / neutral",
    "softness (HSAB)": "Cd (soft) / Co (borderline) / Cr(III) (hard)",
    "substitution kinetics": "Cr(III) inert within 60 s / other cations",
    "redox": "Cr(VI) oxidizes thiols, phenols / As(V)",
    "oxyanion or neutral selectivity": "As(V) vs Cr(VI) (Fe, La); As(III) vs As(V) (thiol)",
}
