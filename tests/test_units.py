# =============================================================================
# test_units.py  –  spectroscopic prefactors (unit conversion itself is tested in tcgm_unitkit)
# =============================================================================
import pytest
from tcgm_unitkit import convert_energy_unit

from cpl50.units import (
    K_DEPS,
    K_EPS,
    K_EPS_D,
    au_dipole_strength_to_cgs40,
    dissymmetry_factor,
    osc_to_dipole_strength,
)


def test_literature_prefactors():
    # f = 4.32e-9 int eps dnu ;  R = 2.296e-39 int deps/nu dnu  (L mol^-1 cm^-1, cm^-1, cgs)
    assert K_EPS == pytest.approx(2.315e8, rel=1e-3)
    assert 1.0 / K_DEPS == pytest.approx(2.296e-39, rel=1e-3)
    assert K_EPS_D == pytest.approx(K_DEPS / 4)


def test_dipole_strength_matches_orca_d2():
    # ORCA 6.1 TDDFT row: E = 3.396117 eV, fosc(D2) = 0.002364012, D2 = 0.02841 au^2
    d = osc_to_dipole_strength(3.396117, 0.002364012)
    assert d == pytest.approx(au_dipole_strength_to_cgs40(0.02841), rel=2e-4)


def test_f_and_d_route_agree():
    # K_EPS f == K_EPS_D nu D at the band centre (same eps from both formulations)
    e_ev, f = 3.0, 0.5
    nu = convert_energy_unit(e_ev, "ev", "cm-1")
    d = osc_to_dipole_strength(e_ev, f) * 1e-40
    assert K_EPS * f == pytest.approx(K_EPS_D * nu * d, rel=1e-8)


def test_dissymmetry_factor():
    assert dissymmetry_factor(1.0, 400.0) == pytest.approx(0.01)
