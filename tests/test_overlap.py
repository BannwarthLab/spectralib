# =============================================================================
# test_overlap.py  –  spectral overlap utilities
# =============================================================================
import numpy as np
import pytest

from cpl50.overlap import (
    align_and_overlap,
    benchmark_summary,
    compute_overlap,
    find_best_shift,
    main_band_sign,
    signs_match,
)
from cpl50.utils import Spectrum


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def make_gaussian(center: float = 2.0, width: float = 0.1) -> tuple:
    """Single Gaussian on an eV grid."""
    x = np.linspace(1.5, 3.5, 401)
    y = np.exp(-0.5 * ((x - center) / width) ** 2)
    return x, y


def make_spectrum(center: float = 2.0, width: float = 0.1) -> Spectrum:
    x, y = make_gaussian(center=center, width=width)
    return Spectrum(x=x, y=y, xunit="ev")


def make_signed_spectrum(
    center_pos: float = 2.0,
    center_neg: float = 2.3,
    width: float = 0.1,
    amp_pos: float = 1.0,
    amp_neg: float = 1.0,
) -> Spectrum:
    """Two-lobe signed spectrum (positive then negative), resembling CPL."""
    x = np.linspace(1.5, 3.5, 401)
    y = (
        amp_pos * np.exp(-0.5 * ((x - center_pos) / width) ** 2)
        - amp_neg * np.exp(-0.5 * ((x - center_neg) / width) ** 2)
    )
    return Spectrum(x=x, y=y, xunit="ev")


# ---------------------------------------------------------------------------
# Unit guard
# ---------------------------------------------------------------------------

def test_compute_overlap_rejects_non_ev():
    """compute_overlap must raise if spectra are not in eV."""
    x = np.linspace(300, 700, 201)
    y = np.exp(-0.5 * ((x - 500) / 20) ** 2)
    spec_nm = Spectrum(x=x, y=y, xunit="nm")
    with pytest.raises(ValueError, match="eV"):
        compute_overlap(spec_nm, spec_nm)


# ---------------------------------------------------------------------------
# Unsigned overlap (cosine)
# ---------------------------------------------------------------------------

def test_unsigned_self_overlap_is_one():
    """Cosine self-overlap must equal exactly 1."""
    ref = make_spectrum()
    assert abs(compute_overlap(ref, ref) - 1.0) < 1e-9


def test_unsigned_antiparallel_is_negative():
    """Inverted unsigned spectrum — cosine overlap must be negative."""
    ref = make_spectrum()
    inv = ref.scale_y(-1.0)
    assert compute_overlap(ref, inv) < 0


def test_unsigned_separated_gaussians_positive():
    """Two separated Gaussians still share positive cosine overlap."""
    ref = make_spectrum(center=2.0)
    tgt = make_spectrum(center=2.4)
    assert compute_overlap(ref, tgt) > 0


def test_unsigned_orthogonal_near_zero():
    """Non-overlapping Gaussians far apart should give near-zero overlap."""
    ref = make_spectrum(center=1.6, width=0.05)
    tgt = make_spectrum(center=3.4, width=0.05)
    assert abs(compute_overlap(ref, tgt)) < 0.01


# ---------------------------------------------------------------------------
# Signed overlap
# ---------------------------------------------------------------------------

# def test_signed_self_overlap_is_one():
#     """Signed self-overlap must equal exactly 1."""
#     ref = make_signed_spectrum()
#     assert abs(compute_overlap(ref, ref, signed=True) - 1.0) < 1e-9


# def test_signed_enantiomer_is_minus_one():
#     """Inverted signed spectrum (enantiomer) must give overlap = -1."""
#     ref = make_signed_spectrum()
#     enan = ref.scale_y(-1.0)
#     assert abs(compute_overlap(ref, enan, signed=True) - (-1.0)) < 1e-9


# def test_signed_unsigned_gives_positive():
#     """Unsigned (LUM-like) vs signed (CPL-like): positive lobe dominates -> > 0."""
#     cpl = make_signed_spectrum(amp_pos=1.0, amp_neg=0.5)
#     lum = make_spectrum(center=2.0)
#     # dominant lobe of cpl is positive, lum is purely positive -> o_pos > o_neg
#     assert compute_overlap(cpl, lum, signed=True) > 0


# def test_signed_no_cross_lobe_contamination():
#     """Spectra with non-overlapping lobes of opposite sign should give 0."""
#     x = np.linspace(1.5, 3.5, 401)
#     # ref: positive lobe only at 2.0
#     y_ref = np.exp(-0.5 * ((x - 2.0) / 0.05) ** 2)
#     # tgt: negative lobe only at 2.5 — zero spatial overlap with ref lobe
#     y_tgt = -np.exp(-0.5 * ((x - 2.5) / 0.05) ** 2)
#     ref = Spectrum(x=x, y=y_ref, xunit="ev")
#     tgt = Spectrum(x=x, y=y_tgt, xunit="ev")
#     # o_pos = 0 (tgt has no positive lobe), o_neg = 0 (ref has no negative lobe)
#     assert compute_overlap(ref, tgt, signed=True) == 0.0


# ---------------------------------------------------------------------------
# find_best_shift
# ---------------------------------------------------------------------------

def test_find_best_shift_identity():
    """Self-shift: best shift must be 0 and overlap ≈ 1."""
    ref = make_spectrum()
    shifts, overlaps = find_best_shift(
        ref, ref, shift_range=np.arange(-0.3, 0.31, 0.01)
    )
    assert abs(shifts[np.argmax(overlaps)]) < 1e-6
    assert overlaps.max() > 0.99


def test_find_best_shift_known_offset():
    """Grid search must recover the true displacement to within step size."""
    ref = make_spectrum(center=2.0)
    tgt = make_spectrum(center=2.2)
    step = 0.01
    shifts, overlaps = find_best_shift(
        ref, tgt, shift_range=np.arange(-0.4, 0.41, step)
    )
    best_shift = shifts[np.argmax(overlaps)]
    # True offset is -0.2 eV (shift tgt left to align with ref)
    assert abs(best_shift - (-0.2)) < 2 * step


def test_find_best_shift_signed():
    """Grid search with signed=True should also recover the true offset."""
    ref = make_signed_spectrum(center_pos=2.0, center_neg=2.3)
    tgt = make_signed_spectrum(center_pos=2.2, center_neg=2.5)
    step = 0.01
    shifts, overlaps = find_best_shift(
        ref, tgt,
        shift_range=np.arange(-0.4, 0.41, step),
        signed=True,
    )
    best_shift = shifts[np.argmax(overlaps)]
    assert abs(best_shift - (-0.2)) < 2 * step


def test_find_best_shift_returns_tuple_of_arrays():
    ref = make_spectrum()
    result = find_best_shift(ref, ref, shift_range=np.arange(-0.1, 0.11, 0.05))
    assert len(result) == 2
    assert isinstance(result[0], np.ndarray)
    assert isinstance(result[1], np.ndarray)
    assert len(result[0]) == len(result[1])


# ---------------------------------------------------------------------------
# align_and_overlap
# ---------------------------------------------------------------------------

def test_align_and_overlap_identity():
    """Self-alignment: shift must be 0, overlap ≈ 1."""
    ref = make_spectrum()
    shift, overlap = align_and_overlap(ref, ref)
    assert abs(shift) < 1e-6
    assert overlap > 0.99


def test_align_and_overlap_recovers_shift():
    """Peak-alignment shift should approximately match the true offset."""
    ref = make_spectrum(center=2.0)
    tgt = make_spectrum(center=2.3)
    shift, overlap = align_and_overlap(ref, tgt)
    assert abs(shift - (-0.3)) < 0.05
    assert overlap > 0.9


# def test_align_and_overlap_signed():
#     ref = make_signed_spectrum(center_pos=2.0, center_neg=2.3)
#     tgt = make_signed_spectrum(center_pos=2.2, center_neg=2.5)
#     shift, overlap = align_and_overlap(ref, tgt, signed=True)
#     assert abs(shift - (-0.2)) < 0.05
#     assert overlap > 0.9


# ---------------------------------------------------------------------------
# main_band_sign and signs_match
# ---------------------------------------------------------------------------

def test_main_band_sign_positive_spectrum():
    ref = make_spectrum()
    assert main_band_sign(ref) == 1


def test_main_band_sign_negative_spectrum():
    ref = make_spectrum().scale_y(-1.0)
    assert main_band_sign(ref) == -1


def test_main_band_sign_dominant_positive_lobe():
    """Larger positive lobe -> sign = +1."""
    cpl = make_signed_spectrum(amp_pos=2.0, amp_neg=1.0)
    assert main_band_sign(cpl) == 1


def test_main_band_sign_dominant_negative_lobe():
    """Larger negative lobe -> sign = -1."""
    cpl = make_signed_spectrum(amp_pos=1.0, amp_neg=2.0)
    assert main_band_sign(cpl) == -1


def test_signs_match_identical():
    ref = make_signed_spectrum()
    assert signs_match(ref, ref)


def test_signs_match_enantiomer():
    ref  = make_signed_spectrum()
    enan = ref.scale_y(-1.0)
    assert not signs_match(ref, enan)

# ---------------------------------------------------------------------------
# benchmark_summary
# ---------------------------------------------------------------------------

def test_benchmark_summary_keys():
    """Summary dict must contain all expected keys."""
    ref = make_signed_spectrum()
    result = benchmark_summary(
        ref, ref,
        shift_range=np.arange(-0.2, 0.21, 0.05),
        signed=True,
    )
    expected = {
        "signs_match", "overlap_pos", "overlap_neg", "best_shift",
        "best_overlap",
    }
    assert expected == set(result.keys())


def test_benchmark_summary_self():
    """Self-benchmark: signs match, overlaps ≈ 1, shift ≈ 0, error ≈ 0."""
    ref = make_signed_spectrum()
    result = benchmark_summary(
        ref, ref,
        shift_range=np.arange(-0.2, 0.21, 0.05),
        signed=True,
    )
    assert result["signs_match"] is True
    assert abs(result["overlap_pos"]  - 1.0) < 1e-6
    assert abs(result["overlap_neg"]  - 1.0) < 1e-6
    assert abs(result["best_overlap"] - 1.0) < 1e-6
    assert abs(result["best_shift"])         < 0.01
    #assert result["peak_position_error"] == 0.0


# def test_benchmark_summary_enantiomer():
#     """Enantiomer: signs do not match, overlap_raw ≈ -1, error is None."""
#     ref  = make_signed_spectrum()
#     enan = ref.scale_y(-1.0)
#     result = benchmark_summary(
#         ref, enan,
#         shift_range=np.arange(-0.2, 0.21, 0.05),
#         signed=True,
#     )
#     assert result["signs_match"] is False
#     assert result["overlap_raw"] < -0.9
#     assert result["peak_position_error"] is None