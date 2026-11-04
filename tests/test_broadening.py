# =============================================================================
# test_broadening.py
# =============================================================================
import numpy as np
import pytest
from scipy.integrate import trapezoid
from scipy.optimize import brentq
from unitkit import convert_energy_unit

from spectralib.broadening import (
    _tch_fwhm,
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
    pseudo_voigt,
    pseudo_voigt_eta,
    sigma_from_fwhm,
    voigt,
    voigt_fwhm,
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


def _numerical_fwhm(shape, *widths):
    half = 0.5 * shape(np.array([0.0]), 0.0, *widths)[0]
    return 2 * brentq(lambda x: shape(np.array([x]), 0.0, *widths)[0] - half, 1e-12, 10 * sum(widths))


@pytest.mark.parametrize("shape", [voigt, pseudo_voigt])
@pytest.mark.parametrize("wg, wl", [(1.0, 0.0), (1.0, 0.3), (1.0, 1.0), (0.3, 1.0), (0.0, 1.0)])
def test_voigt_normalised(shape, wg, wl):
    x = np.linspace(-400, 400, 1600001)
    assert trapezoid(shape(x, 0.0, wg, wl), x) == pytest.approx(1.0, abs=5e-3)  # Lorentzian tails


@pytest.mark.parametrize("wg, wl", [(1.0, 0.0), (1.0, 0.3), (1.0, 1.0), (0.3, 1.0), (0.0, 1.0)])
def test_voigt_fwhm(wg, wl):
    assert _numerical_fwhm(voigt, wg, wl) == pytest.approx(voigt_fwhm(wg, wl), rel=3e-4)  # Olivero-Longbotham
    assert _numerical_fwhm(pseudo_voigt, wg, wl) == pytest.approx(_tch_fwhm(wg, wl), rel=1e-9)  # by construction
    assert _tch_fwhm(wg, wl) == pytest.approx(voigt_fwhm(wg, wl), rel=5e-3)


def test_voigt_limits():
    x = np.linspace(-5, 5, 1001)
    assert voigt(x, 0.5, 1.2, 0.0) == pytest.approx(gaussian(x, 0.5, 1.2))
    assert voigt(x, 0.5, 0.0, 1.2) == pytest.approx(lorentzian(x, 0.5, 1.2))
    assert voigt(x, 0.5, 1.2, 1e-9) == pytest.approx(gaussian(x, 0.5, 1.2), rel=1e-6, abs=1e-9)
    assert voigt_fwhm(1.0, 0.0) == pytest.approx(1.0)
    assert voigt_fwhm(0.0, 1.0) == pytest.approx(1.0, rel=1e-5)  # rounded OL coefficients
    assert pseudo_voigt_eta(1.0, 0.0) == 0.0
    assert pseudo_voigt_eta(0.0, 1.0) == pytest.approx(1.0, abs=1e-5)
    with pytest.raises(ValueError):
        voigt(x, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        pseudo_voigt(x, 0.0, -1.0, 1.0)


@pytest.mark.parametrize("wl", [0.1, 0.5, 1.0, 3.0])
def test_pseudo_voigt_close_to_voigt(wl):
    x = np.linspace(-20, 20, 40001)
    v, pv = voigt(x, 0.0, 1.0, wl), pseudo_voigt(x, 0.0, 1.0, wl)
    assert np.max(np.abs(pv - v)) < 0.02 * v.max()


def test_voigt_matches_numerical_convolution():
    x = np.linspace(-60, 60, 120001)
    dx = x[1] - x[0]
    conv = np.convolve(gaussian(x, 0.0, 1.0), lorentzian(x, 0.0, 0.6), mode="same") * dx
    core = abs(x) < 5
    assert voigt(x, 0.0, 1.0, 0.6)[core] == pytest.approx(conv[core], rel=1e-3)


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


@pytest.mark.parametrize("shape", ["voigt", "pseudo_voigt"])
def test_broaden_voigt_shapes(shape):
    y = broaden([3.0, 5.0], [1.0, -0.5], GRID, (0.2, 0.05), shape=shape)
    assert trapezoid(y, GRID) == pytest.approx(0.5, abs=5e-3)
    ref = voigt if shape == "voigt" else pseudo_voigt
    assert y == pytest.approx(ref(GRID, 3.0, 0.2, 0.05) - 0.5 * ref(GRID, 5.0, 0.2, 0.05))


def test_broaden_width_validation():
    with pytest.raises(ValueError, match="needs 2"):
        broaden([3.0], [1.0], GRID, 0.2, shape="voigt")
    with pytest.raises(ValueError, match="needs 1"):
        broaden([3.0], [1.0], GRID, (0.2, 0.1), shape="gaussian")
    with pytest.raises(ValueError, match="Unknown shape"):
        broaden([3.0], [1.0], GRID, 0.2, shape="sinc")


def test_epsilon_voigt_unit_independent():
    w = (0.3, 0.1)
    spec = epsilon_spectrum([4.0], [0.3], GRID, w, shape="voigt")
    fac = convert_energy_unit(1.0, "ev", "cm-1")
    nu = convert_energy_unit(GRID.copy(), "ev", "cm-1")
    spec_cm = epsilon_spectrum([4.0 * fac], [0.3], nu, (w[0] * fac, w[1] * fac), unit="cm-1", shape="voigt")
    assert spec_cm.y == pytest.approx(spec.y)
