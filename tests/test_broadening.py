# =============================================================================
# test_broadening.py
# =============================================================================
import numpy as np
import pytest
from scipy.integrate import trapezoid

from spectralib.broadening import (
    broaden,
    emission_spectrum,
    fwhm_from_fw1e,
    fwhm_from_sigma,
    gaussian,
    lorentzian,
    sigma_from_fwhm,
)

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


def test_emission_has_cubic_weight():
    spec = emission_spectrum([3.0], [1.0], GRID, 0.3)
    ref = GRID**3 * gaussian(GRID, 3.0, 0.3)
    assert spec.y == pytest.approx(ref)


def test_emission_glum_is_4r_over_d():
    e, f, r = 2.8, 0.05, -12.0  # eV, dimensionless, 1e-40 esu^2 cm^2
    d = 3 * f / (2 * e / 27.211386) * 64604.75  # 1e-40 esu^2 cm^2
    assert d == pytest.approx(47089, rel=1e-4)
    lum = emission_spectrum([e], [d], GRID, 0.35)
    cpl = emission_spectrum([e], [2 * r], GRID, 0.35)
    i = np.argmin(abs(GRID - e))
    assert 2 * cpl.y[i] / lum.y[i] == pytest.approx(4 * r / d)
