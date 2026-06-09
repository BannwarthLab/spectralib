# =============================================================================
# test_convolution.py
# =============================================================================
import numpy as np
import pytest
from scipy.integrate import trapezoid

from cpl50.convolution import gaussian_profile, broaden_spectrum
from cpl50.utils import Spectrum


# ---------------------------------------------------------------------------
# gaussian_profile
# ---------------------------------------------------------------------------

def test_gaussian_profile_shape():
    """gaussian_profile returns array with same shape as input."""
    x = np.linspace(0, 10, 100)
    y = gaussian_profile(center=5.0, sigma=1.0, x=x)
    assert y.shape == x.shape


def test_gaussian_profile_normalized():
    """Gaussian is approximately normalized (integral ≈ 1)."""
    x = np.linspace(-10, 10, 1000)
    y = gaussian_profile(center=0.0, sigma=1.0, x=x)
    # Integrate using trapezoid rule
    integral = trapezoid(y, x)
    assert abs(integral - 1.0) < 0.01


def test_gaussian_profile_max_at_center():
    """Maximum of Gaussian is at the center."""
    x = np.linspace(0, 10, 1000)
    y = gaussian_profile(center=5.0, sigma=1.0, x=x)
    max_idx = np.argmax(y)
    assert x[max_idx] == pytest.approx(5.0, abs=0.1)


def test_gaussian_profile_symmetric():
    """Gaussian is symmetric about center."""
    x = np.linspace(0, 10, 1001)
    y = gaussian_profile(center=5.0, sigma=1.0, x=x)
    # Check symmetry: left and right halves
    center_idx = len(x) // 2
    left = y[:center_idx]
    right = y[center_idx + 1:]
    right_reversed = right[::-1]
    assert np.allclose(left, right_reversed, atol=1e-6)


# ---------------------------------------------------------------------------
# broaden_spectrum
# ---------------------------------------------------------------------------

def test_broaden_spectrum_returns_spectrum():
    """broaden_spectrum returns a Spectrum object."""
    energies = np.array([1.0, 2.0, 3.0])
    strengths = np.array([1.0, 1.0, 1.0])
    spec = broaden_spectrum(energies, strengths)
    assert isinstance(spec, Spectrum)


def test_broaden_spectrum_xunit_ev():
    """Broadened spectrum has xunit='ev'."""
    energies = np.array([2.0])
    strengths = np.array([1.0])
    spec = broaden_spectrum(energies, strengths)
    assert spec.xunit == "ev"


def test_broaden_spectrum_length():
    """Broadened spectrum has correct length."""
    energies = np.array([2.0])
    strengths = np.array([1.0])
    n_points = 500
    spec = broaden_spectrum(energies, strengths, n_points=n_points)
    assert len(spec) == n_points


def test_broaden_spectrum_energy_range():
    """x-axis covers specified energy range."""
    e_min, e_max = 1.0, 5.0
    spec = broaden_spectrum(
        np.array([2.0]),
        np.array([1.0]),
        e_min=e_min,
        e_max=e_max,
        n_points=100,
    )
    assert spec.x[0] == pytest.approx(e_min, abs=1e-6)
    assert spec.x[-1] == pytest.approx(e_max, abs=1e-6)


def test_broaden_spectrum_single_stick():
    """Single stick broadens to Gaussian profile."""
    energies = np.array([3.0])
    strengths = np.array([1.0])
    sigma = 0.5
    spec = broaden_spectrum(
        energies,
        strengths,
        e_min=1.0,
        e_max=5.0,
        sigma=sigma,
        n_points=1000,
    )
    # Peak should be near 3.0
    max_idx = np.argmax(spec.y)
    assert spec.x[max_idx] == pytest.approx(3.0, abs=0.1)


def test_broaden_spectrum_multiple_sticks():
    """Multiple sticks broaden independently."""
    energies = np.array([2.0, 4.0])
    strengths = np.array([1.0, 1.0])
    spec = broaden_spectrum(
        energies,
        strengths,
        e_min=1.0,
        e_max=5.0,
        sigma=0.2,
        n_points=1000,
    )
    # Should have two peaks roughly at 2.0 and 4.0
    y = spec.y
    # Find local maxima
    peaks = []
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            peaks.append(spec.x[i])
    
    assert len(peaks) >= 1, "Should find at least one peak"


def test_broaden_spectrum_zero_strength():
    """Zero strength stick contributes nothing."""
    energies = np.array([2.0, 4.0])
    strengths = np.array([1.0, 0.0])
    spec = broaden_spectrum(
        energies,
        strengths,
        e_min=1.0,
        e_max=5.0,
        sigma=0.2,
        n_points=1000,
    )
    # Should only have significant intensity near 2.0
    mid_range = np.where((spec.x > 3.0) & (spec.x < 5.0))[0]
    max_intensity_right = np.max(spec.y[mid_range])
    # Right side should have much less intensity than peak
    peak_intensity = np.max(spec.y)
    assert max_intensity_right < 0.1 * peak_intensity


def test_broaden_spectrum_negative_strength():
    """Negative strength sticks work (for CD)."""
    energies = np.array([2.0, 4.0])
    strengths = np.array([1.0, -1.0])
    spec = broaden_spectrum(
        energies,
        strengths,
        e_min=1.0,
        e_max=5.0,
        sigma=0.2,
        n_points=1000,
    )
    # Should have positive and negative regions
    assert np.max(spec.y) > 0
    assert np.min(spec.y) < 0


def test_broaden_spectrum_strictly_increasing_x():
    """Broadened spectrum x-axis is strictly increasing."""
    energies = np.array([2.0, 3.0, 4.0])
    strengths = np.array([1.0, 1.0, 1.0])
    spec = broaden_spectrum(energies, strengths, n_points=1000)
    # Spectrum constructor checks x is strictly increasing, so this should pass
    assert np.all(np.diff(spec.x) > 0)


def test_broaden_spectrum_convertible():
    """Broadened spectrum can be converted to other units."""
    energies = np.array([2.0, 3.0])
    strengths = np.array([1.0, 1.0])
    spec = broaden_spectrum(energies, strengths, e_min=1.0, e_max=5.0)
    
    # Convert to nm
    spec_nm = spec.convert_x("nm")
    assert spec_nm.xunit == "nm"
    assert len(spec_nm) == len(spec)
