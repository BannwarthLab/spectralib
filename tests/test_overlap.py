# =============================================================================
# test_overlap.py  –  spectral overlap utilities
# =============================================================================
import numpy as np

from cpl50.overlap import compute_overlap, find_best_shift
from cpl50.utils import Spectrum


def make_gaussian(center: float = 0.5, width: float = 0.1):
    x = np.linspace(0.0, 1.0, 201)
    y = np.exp(-0.5 * ((x - center) / width) ** 2)
    return x, y


def make_spectrum(center: float = 0.5, width: float = 0.1) -> Spectrum:
    x, y = make_gaussian(center=center, width=width)
    return Spectrum(x=x, y=y, metadata={})


# ---------------------------------------------------------------------------
# find_best_shift
# ---------------------------------------------------------------------------

def test_find_best_shift_identity():
    """Shifting a spectrum against itself should recover shift=0, overlap≈1."""
    ref = make_spectrum()
    shifts, overlaps = find_best_shift(
        ref, ref,
        shift_range=np.arange(-0.5, 0.51, 0.05),
        overlap_mode="area",
    )
    best_shift = shifts[np.argmax(overlaps)]
    best_overlap = overlaps.max()
    assert abs(best_shift) < 1e-6
    assert best_overlap > 0.99


def test_find_best_shift_known_offset():
    """Best shift should approximately recover the true displacement."""
    ref = make_spectrum(center=0.4)
    tgt = make_spectrum(center=0.6)
    shift_range = np.arange(-0.3, 0.31, 0.01)
    shifts, overlaps = find_best_shift(ref, tgt, shift_range=shift_range, overlap_mode="area")
    best_shift = shifts[np.argmax(overlaps)]
    # True offset is −0.2 (shift tgt left to align with ref)
    assert abs(best_shift - (-0.2)) < 0.02


# ---------------------------------------------------------------------------
# compute_overlap modes
# ---------------------------------------------------------------------------

def test_cosine_overlap_antiparallel_is_negative():
    x = np.linspace(0.0, 1.0, 201)
    y = np.sin(2 * np.pi * x)
    pos = Spectrum(x=x, y=y,  metadata={})
    neg = Spectrum(x=x, y=-y, metadata={})
    assert compute_overlap(pos, neg, mode="cosine") < 0


def test_absolute_overlap_antiparallel_is_positive():
    x = np.linspace(0.0, 1.0, 201)
    y = np.sin(2 * np.pi * x)
    pos = Spectrum(x=x, y=y,  metadata={})
    neg = Spectrum(x=x, y=-y, metadata={})
    assert compute_overlap(pos, neg, mode="absolute") > 0


def test_area_overlap_separated_gaussians_positive():
    """Two non-overlapping Gaussians still share positive area overlap."""
    ref = make_spectrum(center=0.4)
    tgt = make_spectrum(center=0.6)
    assert compute_overlap(ref, tgt, mode="area") > 0


def test_overlap_identical_spectra_maximum(valid_header=None):
    """Self-overlap should equal 1 for cosine mode."""
    ref = make_spectrum()
    assert abs(compute_overlap(ref, ref, mode="cosine") - 1.0) < 1e-9