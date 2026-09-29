"""Spectroscopic prefactors built from the ``tcgm_unitkit`` physical constants.

Energy-axis conversions use ``tcgm_unitkit.convert_energy_unit`` directly.

Conventions for transition quantities:
    f    oscillator strength (dimensionless)
    D    dipole strength |<0|mu|n>|^2,             reported in 1e-40 esu^2 cm^2
    R    rotatory strength Im(<0|mu|n>.<n|m|0>),    reported in 1e-40 esu^2 cm^2
         (the "R (1e40*cgs)" column of ORCA/Turbomole)
With D and R in the same units, the dissymmetry factor is g = 4 R / D.
"""

from __future__ import annotations

import numpy as np
from tcgm_unitkit import convert_energy_unit, convert_length_unit
from tcgm_unitkit.constants.physical_constants import (
    AVOGADRO_CONSTANT,
    ELECTRON_MASS,
    ELEMENTARY_CHARGE,
    H_PLANCK,
    PI,
    SPEED_OF_LIGHT,
    VACUUM_PERMITTIVITY,
)

_LN10 = np.log(10.0)

# cgs constants (erg s, cm/s, esu) derived from the SI values in tcgm_unitkit
_H_CGS = H_PLANCK * 1e7
_C_CGS = SPEED_OF_LIGHT * 1e2
_ME_CGS = ELECTRON_MASS * 1e3
_E_ESU = ELEMENTARY_CHARGE * _C_CGS / 10.0  # 1 C = c_cgs/10 esu

#: 1e-40 esu^2 cm^2, the customary unit of D and R
CGS40 = 1e-40

#: eps(nu) = K_EPS * f * g(nu), g normalised in cm^-1  ->  eps in L mol^-1 cm^-1.
#: SI: N_A e^2 / (4 eps0 m_e c^2 ln10) [m mol^-1]; x10 (m^2/mol -> L mol^-1 cm^-1), x1e-2 (m^-1 -> cm^-1).
#: Integrated form: f = int eps dnu / K_EPS  (K_EPS = 2.315e8 L mol^-1 cm^-2).
K_EPS = (
    AVOGADRO_CONSTANT * ELEMENTARY_CHARGE**2
    / (4.0 * VACUUM_PERMITTIVITY * ELECTRON_MASS * SPEED_OF_LIGHT**2 * _LN10)
    * 10.0 * 1e-2
)

#: delta_eps(nu) = K_DEPS * nu * R * g(nu), nu in cm^-1, R in esu^2 cm^2  ->  L mol^-1 cm^-1.
#: cgs: 32 pi^3 N_A / (3000 ln10 h c)   (Rosenfeld; 1000 converts cm^3 -> L).
#: Integrated form: R = 2.296e-39 int delta_eps / nu dnu.
K_DEPS = 32.0 * PI**3 * AVOGADRO_CONSTANT / (3000.0 * _LN10 * _H_CGS * _C_CGS)

#: Same prefactor for absorption written with D:  eps(nu) = K_DEPS / 4 * nu * D * g(nu).
K_EPS_D = K_DEPS / 4.0


def osc_to_dipole_strength(energy_ev: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Dipole strength D in 1e-40 esu^2 cm^2 from oscillator strength.

    D = 3 h e^2 f / (8 pi^2 m_e c nu)   (cgs, nu in cm^-1)
    equivalently D[a.u.] = 3 f / (2 dE[Eh]).
    """
    nu = convert_energy_unit(np.array(energy_ev, dtype=float), "ev", "cm-1")
    d = 3.0 * _H_CGS * _E_ESU**2 * np.asarray(f, dtype=float) / (8.0 * PI**2 * _ME_CGS * _C_CGS * nu)
    return d / CGS40


def au_dipole_strength_to_cgs40(d_au: np.ndarray) -> np.ndarray:
    """Convert |mu|^2 from (e a0)^2 to 1e-40 esu^2 cm^2."""
    ea0_esu_cm = _E_ESU * convert_length_unit(1.0, "bohr", "cm")
    return np.asarray(d_au, dtype=float) * ea0_esu_cm**2 / CGS40


def dissymmetry_factor(r: np.ndarray, d: np.ndarray) -> np.ndarray:
    """g = 4 R / D (g_abs or, at the emitting geometry, g_lum). R and D in the same units."""
    return 4.0 * np.asarray(r, dtype=float) / np.asarray(d, dtype=float)
