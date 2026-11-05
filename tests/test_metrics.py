# =============================================================================
# test_metrics.py
# =============================================================================
import numpy as np
import pytest

from spectralib.metrics import (
    benchmark,
    cosine,
    dominant_sign,
    e_ene,
    e_spe,
    lobe_cosines,
    optimal_shift,
    peak_energy,
    sign_ratio,
    signs_match,
)
from spectralib.spectrum import Spectrum

X = np.linspace(1.5, 3.5, 801)


def band(c, w=0.1, a=1.0, x=X):
    return a * np.exp(-0.5 * ((x - c) / w) ** 2)


def spec(y, x=X):
    return Spectrum(x, y, xunit="ev")


def couplet(c1=2.0, c2=2.3, a1=1.0, a2=1.0):
    return spec(band(c1, a=a1) - band(c2, a=a2))


def test_rejects_non_ev():
    s = Spectrum(np.linspace(300, 700, 50), np.ones(50))
    with pytest.raises(ValueError, match="eV"):
        cosine(s, s)


def test_cosine_identity_enantiomer_scale():
    ref = couplet()
    assert cosine(ref, ref) == pytest.approx(1.0)
    assert cosine(ref, ref.scale_y(-3.0)) == pytest.approx(-1.0)
    assert cosine(ref, ref.scale_y(1e-5)) == pytest.approx(1.0)


def test_lobes_monosignate_self_is_one_not_half():
    ref = spec(band(2.5))
    o_pos, o_neg = lobe_cosines(ref, ref)
    assert o_pos == pytest.approx(1.0)
    assert np.isnan(o_neg)
    assert optimal_shift(ref, ref, (-0.1, 0.1), objective="lobes")[1] == pytest.approx(1.0)


def test_lobes_enantiomer_zero():
    ref = couplet()
    assert lobe_cosines(ref, ref.scale_y(-1)) == pytest.approx((0.0, 0.0), abs=1e-3)


def test_e_spe_limits():
    ref = couplet()
    assert e_spe(ref, ref) == pytest.approx(0.0)
    assert e_spe(ref, ref.scale_y(7.0)) == pytest.approx(0.0)  # area normalisation
    assert e_spe(ref, ref.scale_y(-1.0)) == pytest.approx(2.0)
    assert e_spe(spec(band(1.8, 0.05)), spec(band(3.2, 0.05))) == pytest.approx(2.0, abs=1e-6)
    assert e_spe(ref, ref.scale_y(2.0), norm=None) == pytest.approx(1.0)


@pytest.mark.parametrize("objective", ["cosine", "abs_cosine", "lobes", "e_spe"])
def test_optimal_shift_recovers_offset(objective):
    ref = couplet(2.0, 2.3)
    calc = couplet(2.23, 2.53)  # true shift -0.23
    s, _ = optimal_shift(ref, calc, (-0.5, 0.5), step=0.01, objective=objective)
    assert s == pytest.approx(-0.23, abs=2e-3)


def test_window_ref_ignores_calc_outside_measurement():
    xr = np.linspace(2.0, 3.0, 401)
    ref = spec(band(2.5, x=xr), x=xr)
    calc = spec(band(2.5) + band(1.6))  # extra band outside the measured window
    assert cosine(ref, calc, window="ref") == pytest.approx(1.0, abs=1e-6)
    assert cosine(ref, calc, window="union") < 0.8


def test_sign_helpers():
    pos = couplet(a1=2.0)
    neg = couplet(a2=2.0)
    assert dominant_sign(pos) == 1 and dominant_sign(neg) == -1
    assert not signs_match(pos, neg)
    assert sign_ratio(spec(band(2.5))) == pytest.approx(1.0)
    assert abs(sign_ratio(couplet())) < 1e-6
    assert peak_energy(neg) == pytest.approx(2.3, abs=0.005)


def test_e_ene():
    assert e_ene([3.0, 4.0], [3.1, 3.9]) == pytest.approx(0.1)
    # root flipping: matched assignment pairs 3.0<->3.05, 3.2<->3.25
    assert e_ene([3.0, 3.2], [3.25, 3.05], match=True) == pytest.approx(0.05)
    with pytest.raises(ValueError):
        e_ene([1.0], [1.0, 2.0])


def test_benchmark_signed():
    ref = couplet(2.0, 2.3, a1=1.5)
    calc = couplet(2.2, 2.5, a1=1.5).scale_y(10)
    res = benchmark(ref, calc, signed=True, bounds=(-0.5, 0.5))
    assert res["shift"] == pytest.approx(-0.2, abs=2e-3)
    assert res["signs_match"] is True
    assert res["cosine"] == pytest.approx(1.0, abs=1e-4)
    assert res["e_spe"] == pytest.approx(0.0, abs=1e-2)
    assert res["peak_error"] == pytest.approx(0.2, abs=0.005)

    enan = benchmark(ref, calc.scale_y(-1), signed=True, bounds=(-0.5, 0.5))
    assert enan["shift"] == pytest.approx(-0.2, abs=2e-3)  # |y| alignment is sign-agnostic
    assert enan["signs_match"] is False
    assert enan["cosine"] == pytest.approx(-1.0, abs=1e-4)


def test_benchmark_given_shift_and_unsigned_keys():
    ref = spec(band(2.5))
    res = benchmark(ref, ref, signed=False, shift=0.0)
    assert set(res) == {"peak_error", "shift", "cosine", "e_spe"}


def test_smoothed_peak_ignores_noise_spike():
    y = band(2.5, w=0.15)
    y[100] = 3.0  # spike at x=1.75
    s = spec(y)
    assert peak_energy(s) == pytest.approx(X[100])
    assert peak_energy(s, smooth_fwhm=0.1) == pytest.approx(2.5, abs=0.01)
