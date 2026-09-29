# =============================================================================
# test_units.py  –  conversions and spectroscopic prefactors
# =============================================================================
import numpy as np
import pytest

from cpl50.io_orca import read_orca_tddft
from cpl50.units import (
    K_DEPS,
    K_EPS,
    K_EPS_D,
    au_dipole_strength_to_cgs40,
    convert_x,
    dissymmetry_factor,
    osc_to_dipole_strength,
    x_jacobian,
)


def test_convert_roundtrip_and_no_mutation():
    x = np.array([250.0, 400.0, 700.0])
    x0 = x.copy()
    ev = convert_x(x, "nm", "ev")
    assert np.array_equal(x, x0)  # tcgm_unitkit modifies in place; the wrapper must not
    assert convert_x(ev, "ev", "nm") == pytest.approx(x)
    assert convert_x(1.0, "ev", "nm") == pytest.approx(1239.84198, rel=1e-8)
    assert convert_x(1.0, "ev", "cm-1") == pytest.approx(8065.54394, rel=1e-8)


def test_convert_rejects_unknown_unit_and_zero():
    with pytest.raises(ValueError):
        convert_x(1.0, "ev", "kcal")
    with pytest.raises(ValueError):
        convert_x(np.array([0.0, 1.0]), "ev", "nm")


def test_jacobian_shape():
    x = np.array([400.0, 800.0])
    assert x_jacobian(x, "nm", "ev") == pytest.approx(x**2)
    assert x_jacobian(x, "ev", "cm-1") == pytest.approx([1.0, 1.0])


def test_literature_prefactors():
    # f = 4.32e-9 int eps dnu ;  R = 2.296e-39 int deps/nu dnu  (L mol^-1 cm^-1, cm^-1, cgs)
    assert K_EPS == pytest.approx(2.315e8, rel=1e-3)
    assert 1.0 / K_DEPS == pytest.approx(2.296e-39, rel=1e-3)
    assert K_EPS_D == pytest.approx(K_DEPS / 4)


def test_dipole_strength_matches_orca_d2():
    # ORCA prints D2 in au^2 next to fosc: 0.02841 for the first root of tmp_orca.out
    tab = read_orca_tddft("tests/tmp_orca.out")
    d = osc_to_dipole_strength(tab["energy"][0], tab["f_len"][0])
    assert d == pytest.approx(au_dipole_strength_to_cgs40(0.02841), rel=2e-4)


def test_f_and_d_route_agree():
    # K_EPS f == K_EPS_D nu D  at the band centre (same eps from both formulations)
    e_ev, f = 3.0, 0.5
    nu = convert_x(e_ev, "ev", "cm-1")
    d = osc_to_dipole_strength(e_ev, f) * 1e-40
    assert K_EPS * f == pytest.approx(K_EPS_D * nu * d, rel=1e-9)


def test_dissymmetry_factor():
    assert dissymmetry_factor(1.0, 400.0) == pytest.approx(0.01)
