import numpy as np

from cpl50.overlap import compute_overlap, find_best_shift
from cpl50.utils import Spectrum


def make_gaussian(center: float = 0.5, width: float = 0.1):
    x = np.linspace(0.0, 1.0, 201)
    y = np.exp(-0.5 * ((x - center) / width) ** 2)
    return x, y


def make_spectrum(center: float = 0.5, width: float = 0.1):
    x, y = make_gaussian(center=center, width=width)
    return Spectrum(x=x, y=y, metadata={})


def test_find_best_shift_identity():
    reference = make_spectrum()
    shifts, overlaps = find_best_shift(
        reference,
        reference,
        shift_range=np.arange(-0.5, 0.51, 0.05),
        overlap_mode="area",
    )
    best_idx = np.argmax(overlaps)
    best_shift = shifts[best_idx]
    best_overlap = overlaps[best_idx]

    assert abs(best_shift) < 1e-6
    assert best_overlap > 0.99


def test_overlap_modes_signed_behavior():
    x = np.linspace(0.0, 1.0, 201)
    y_pos = np.sin(2 * np.pi * x)
    y_neg = -y_pos

    overlap_cosine = compute_overlap(
        Spectrum(x=x, y=y_pos, metadata={}),
        Spectrum(x=x, y=y_neg, metadata={}),
        mode="cosine",
    )
    overlap_absolute = compute_overlap(
        Spectrum(x=x, y=y_pos, metadata={}),
        Spectrum(x=x, y=y_neg, metadata={}),
        mode="absolute",
    )

    assert overlap_cosine < 0
    assert overlap_absolute > 0


def test_area_mode_positive_signals():
    ref = make_spectrum(center=0.4)
    tgt = make_spectrum(center=0.6)
    overlap = compute_overlap(ref, tgt, mode="area")
    assert overlap > 0
