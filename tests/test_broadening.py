# =============================================================================
# test_broadening.py
# =============================================================================
import numpy as np
import pytest
from scipy.integrate import trapezoid
from unitkit import convert_energy_unit

from spectralib.broadening import (
    broaden,
    delta_epsilon_spectrum,
    emission_spectrum,
    ensemble_sticks,
    epsilon_spectrum,
    epsilon_spectrum_from_d,
    fwhm_from_fw1e,
    fwhm_from_sigma,
    gaussian,
    lorentzian,
    sigma_from_fwhm,
)
from spectralib.units import K_EPS, osc_to_dipole_strength

GRID = np.linspace(0.5, 8.0, 7501)


@pytest.mark.parametrize("shape", [gaussian, lorentzian])
def test_lineshape_normalised_with_correct_fwhm(shape):
    x = np.linspace(-200, 200, 400001)
    y = shape(x, 0.0, 2.0)
    tol = 1e-6 if shape is gaussian else 5e-3  # Lorentzian tails
    assert trapezoid(y, x) == pytest.approx(1.0, abs=tol)
    assert shape(np.array([1.0]), 0.0, 2.0)[0] == pytest.approx(0.5 * y.max())


def test_width_conversions():
    assert fwhm_from_sigma(1.0) == pytest.approx(2.35482, rel=1e-5)
    assert sigma_from_fwhm(fwhm_from_sigma(0.7)) == pytest.approx(0.7)
    # Gaussian value at +-FW1e/2 is 1/e of the maximum
    fw1e = 0.5
    w = fwhm_from_fw1e(fw1e)
    assert gaussian(np.array([fw1e / 2]), 0.0, w)[0] / gaussian(np.array([0.0]), 0.0, w)[0] == pytest.approx(np.exp(-1))


def test_broaden_conserves_sum_and_sign():
    y = broaden([3.0, 5.0], [1.0, -0.5], GRID, 0.2)
    assert trapezoid(y, GRID) == pytest.approx(0.5, abs=1e-6)
    assert y[np.argmin(abs(GRID - 5.0))] < 0


def test_ensemble_sticks_weights():
    e, s = ensemble_sticks([([2.0], [1.0]), ([2.1, 3.0], [1.0, 2.0])])
    assert e.tolist() == [2.0, 2.1, 3.0]
    assert s.tolist() == [0.5, 0.5, 1.0]


def test_epsilon_integrates_to_oscillator_strength():
    f = 0.3
    spec = epsilon_spectrum([4.0], [f], GRID, 0.3)
    nu = convert_energy_unit(GRID.copy(), "ev", "cm-1")
    assert trapezoid(spec.y, nu) / K_EPS == pytest.approx(f, rel=1e-6)
    # unit independence: same eps on a cm-1 grid
    spec_cm = epsilon_spectrum(convert_energy_unit(4.0, "ev", "cm-1"), [f], nu, 0.3 * convert_energy_unit(1.0, "ev", "cm-1"), unit="cm-1")
    assert spec_cm.y == pytest.approx(spec.y)


def test_delta_epsilon_rosenfeld_sum_rule():
    r = 100.0  # 1e-40 cgs
    spec = delta_epsilon_spectrum([4.0], [r], GRID, 0.3)
    nu = convert_energy_unit(GRID.copy(), "ev", "cm-1")
    assert 2.296e-39 * trapezoid(spec.y / nu, nu) == pytest.approx(r * 1e-40, rel=1e-3)


def test_gabs_ratio_is_4r_over_d():
    e, f, r = 3.5, 0.1, 50.0
    d = osc_to_dipole_strength(e, f)
    g = delta_epsilon_spectrum([e], [r], GRID, 0.3).y / epsilon_spectrum_from_d([e], [d], GRID, 0.3).y
    assert g[np.argmin(abs(GRID - e))] == pytest.approx(4 * r / d)


def test_emission_has_cubic_weight():
    spec = emission_spectrum([3.0], [1.0], GRID, 0.3)
    ref = GRID**3 * gaussian(GRID, 3.0, 0.3)
    assert spec.y == pytest.approx(ref)

