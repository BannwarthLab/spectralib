# =============================================================================
# test_spectrum.py
# =============================================================================
import numpy as np
import pytest
from scipy.integrate import trapezoid

from cpl50.io import read_spectrum
from cpl50.spectrum import Spectrum


def test_validation():
    with pytest.raises(ValueError):
        Spectrum(np.array([1.0, 2.0]), np.array([1.0]))
    with pytest.raises(ValueError):
        Spectrum(np.array([2.0, 1.0]), np.array([1.0, 1.0]))
    with pytest.raises(ValueError):
        Spectrum(np.array([1.0, 2.0]), np.array([1.0, 1.0]), xunit="hz")


def test_convert_roundtrip_reorders_and_keeps_metadata():
    s = read_spectrum("data/spectra/1/1_CPL.csv")
    ev = s.convert_x("ev")
    assert ev.xunit == "ev" and np.all(np.diff(ev.x) > 0)
    assert ev.y[0] == s.y[-1]
    assert ev.metadata["molname"] == s.metadata["molname"]
    back = ev.convert_x("nm")
    assert back.x == pytest.approx(s.x) and back.y == pytest.approx(s.y)


def test_jacobian_preserves_integral():
    # a density per nm integrated over nm equals the transformed density integrated over eV
    x = np.linspace(350, 700, 5001)
    s = Spectrum(x, np.exp(-0.5 * ((x - 500) / 30) ** 2))
    ev = s.convert_x("ev", jacobian=True)
    ratio = trapezoid(ev.y, ev.x) / trapezoid(s.y, s.x)
    ev2 = Spectrum(x, 2 * s.y).convert_x("ev", jacobian=True)
    assert trapezoid(ev2.y, ev2.x) / trapezoid(2 * s.y, x) == pytest.approx(ratio, rel=1e-6)
    # shape changes: peak moves compared to plain conversion
    assert ev.x[np.argmax(ev.y)] != s.convert_x("ev").x[np.argmax(s.convert_x("ev").y)]


def test_normalize():
    x = np.linspace(0, 1, 101)
    s = Spectrum(x, -3 * np.sin(np.pi * x), xunit="ev")
    assert s.normalize("max").y.min() == pytest.approx(-1.0)
    assert trapezoid(np.abs(s.normalize("area").y), x) == pytest.approx(1.0)


def test_call_interpolates_zero_outside():
    s = Spectrum(np.array([1.0, 2.0]), np.array([1.0, 3.0]), xunit="ev")
    assert s(np.array([0.0, 1.5, 3.0])).tolist() == [0.0, 2.0, 0.0]
