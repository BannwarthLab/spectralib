"""Utilities for computing spectral overlap and optimal energy shift.

All public functions require spectra expressed in eV. Call spec.to_ev()
before passing a spectrum read from a .csv file (which is in nm by default).

Signed spectra (CPL):
    Overlap is reported as two separate cosine similarities, one per lobe
    (o_pos, o_neg). Combined with signs_match(), this gives the complete
    picture without the cancellation problems of a single scalar measure.

    For a correct model:  o_pos ≈ 1, o_neg ≈ 1, signs_match = True
    For an enantiomer:    o_pos ≈ 0, o_neg ≈ 0, signs_match = False
    For wrong shape:      o_pos < 1, o_neg < 1, signs_match = True/False

Unsigned spectra (LUM):
    Single cosine similarity in [0, 1].
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
from typing import Optional, Tuple

from cpl50.utils import Spectrum


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_ev(*spectra: Spectrum) -> None:
    """Raise ValueError if any spectrum is not in eV."""
    for spec in spectra:
        if spec.xunit != "ev":
            raise ValueError(
                f"Spectrum must be in eV before computing overlap "
                f"(got xunit='{spec.xunit}'). Call spec.to_ev() first."
            )


def _interpolate(x: np.ndarray, y: np.ndarray, x_new: np.ndarray) -> np.ndarray:
    """Interpolate y onto x_new using cubic splines, zero outside range.

    Args:
        x (np.ndarray): Original x values.
        y (np.ndarray): Original y values.
        x_new (np.ndarray): Target x grid.

    Returns:
        np.ndarray: Interpolated y values on x_new.
    """
    return interp1d(x, y, kind="cubic", bounds_error=False, fill_value=0.0)(x_new)


def _uniform_grid(
    x_ref: np.ndarray,
    x_tar: np.ndarray,
    n_points: int,
    shift_min: float = 0.0,
    shift_max: float = 0.0,
) -> np.ndarray:
    """Uniform grid spanning both spectra with optional shift margin.

    Args:
        x_ref (np.ndarray): x values of reference spectrum.
        x_tar (np.ndarray): x values of target spectrum.
        n_points (int): Number of grid points.
        shift_min (float): Lower shift bound to extend grid for.
        shift_max (float): Upper shift bound to extend grid for.

    Returns:
        np.ndarray: Uniform grid in eV.
    """
    x_min = min(x_ref.min(), x_tar.min() + shift_min)
    x_max = max(x_ref.max(), x_tar.max() + shift_max)
    return np.linspace(x_min, x_max, n_points)


def _cosine(x: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two non-negative arrays on a shared grid.

    Uses L2 normalisation:
        O = integral(a*b) / sqrt(integral(a^2) * integral(b^2))

    Returns 0.0 if either norm is zero (no signal in that lobe).

    Args:
        x (np.ndarray): Shared x grid.
        a (np.ndarray): First non-negative array.
        b (np.ndarray): Second non-negative array.

    Returns:
        float: Cosine similarity in [0, 1].
    """
    na = np.sqrt(trapezoid(a * a, x))
    nb = np.sqrt(trapezoid(b * b, x))
    if na == 0 or nb == 0:
        return 0.0
    return float(trapezoid(a * b, x) / (na * nb))


def _lobe_overlaps(
    x: np.ndarray,
    y1: np.ndarray,
    y2: np.ndarray,
) -> Tuple[float, float]:
    """Cosine similarity of positive and negative lobes separately.

    Each spectrum is decomposed pointwise into positive and negative parts.
    np.maximum/minimum operate on the full interpolated grid so any number
    of sign changes (n lobes) is handled without special casing.

    Matching-sign lobe magnitudes are compared:
        o_pos: cosine similarity of positive parts of y1 and y2
        o_neg: cosine similarity of negative parts (as magnitudes) of y1 and y2

    For an enantiomeric pair (y2 = -y1):
        y2_pos = |y1_neg|  and  y2_neg = |y1_pos|
        -> o_pos compares y1_pos vs y1_neg_magnitude: zero if lobes don't overlap
        -> o_neg compares y1_neg_magnitude vs y1_pos: zero if lobes don't overlap
        -> both are 0 for well-separated lobes, correctly indicating no match.

    Args:
        x (np.ndarray): Shared x grid.
        y1 (np.ndarray): Reference signed spectrum.
        y2 (np.ndarray): Target signed spectrum.

    Returns:
        Tuple[float, float]: (o_pos, o_neg), each in [0, 1].
    """
    return (
        _cosine(x, np.maximum(y1, 0),         np.maximum(y2, 0)),
        _cosine(x, np.abs(np.minimum(y1, 0)), np.abs(np.minimum(y2, 0))),
    )


def _dominant_lobe_centroid(x: np.ndarray, y: np.ndarray) -> Tuple[float, int]:
    """Centroid and sign of the dominant (largest absolute area) lobe.

    Args:
        x (np.ndarray): x values in eV.
        y (np.ndarray): y values (may be signed).

    Returns:
        Tuple[float, int]: (centroid in eV, sign: +1 or -1).
    """
    pos_area = trapezoid(np.maximum(y, 0), x)
    neg_area = trapezoid(np.abs(np.minimum(y, 0)), x)

    if pos_area >= neg_area:
        mask, sign = y > 0, 1
    else:
        mask, sign = y < 0, -1

    if not mask.any():
        return float(x[np.argmax(np.abs(y))]), sign

    centroid = float(
        trapezoid(x[mask] * np.abs(y[mask]), x[mask])
        / trapezoid(np.abs(y[mask]), x[mask])
    )
    return centroid, sign


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_overlap(
    ref: Spectrum,
    target: Spectrum,
    n_points: int = 1000,
    signed: bool = False,
) -> float | Tuple[float, float]:
    """Compute normalised spectral overlap between ref and target.

    Both spectra must be in eV.

    Unsigned (signed=False):
        Returns a single cosine similarity in [-1, 1]. Suitable for LUM.

    Signed (signed=True):
        Returns (o_pos, o_neg), each in [0, 1] — the cosine similarity of
        the positive and negative lobes separately. Suitable for CPL.
        Interpret together with signs_match():
            o_pos ≈ 1, o_neg ≈ 1, signs_match = True  -> good model
            o_pos ≈ 0, o_neg ≈ 0, signs_match = False -> enantiomer
            mixed values                               -> partial/shifted match

    Args:
        ref (Spectrum): Reference spectrum, xunit='ev'.
        target (Spectrum): Target spectrum, xunit='ev'.
        n_points (int): Number of interpolation grid points.
        signed (bool): If True, return two-lobe overlap tuple.

    Returns:
        float: Cosine similarity (unsigned).
        Tuple[float, float]: (o_pos, o_neg) lobe overlaps (signed).

    Raises:
        ValueError: If either spectrum is not in eV.
    """
    _check_ev(ref, target)
    x_grid = _uniform_grid(ref.x, target.x, n_points)
    y1 = _interpolate(ref.x, ref.y, x_grid)
    y2 = _interpolate(target.x, target.y, x_grid)
    if signed:
        return _lobe_overlaps(x_grid, y1, y2)
    return _cosine(x_grid, y1, y2)


def align_and_overlap(
    ref: Spectrum,
    target: Spectrum,
    n_points: int = 1000,
    signed: bool = False,
) -> Tuple[float, float | Tuple[float, float]]:
    """Align target to reference by dominant peak, then compute overlap.

    Faster than find_best_shift for a first-pass assessment. The shift is
    computed analytically from dominant-lobe centroids (signed) or global
    maxima (unsigned).

    Args:
        ref (Spectrum): Reference spectrum, xunit='ev'.
        target (Spectrum): Target spectrum, xunit='ev'.
        n_points (int): Number of interpolation grid points.
        signed (bool): Use dominant-lobe centroid alignment and lobe overlap.

    Returns:
        Tuple: (shift in eV, overlap).
            overlap is float (unsigned) or Tuple[float,float] (signed).

    Raises:
        ValueError: If either spectrum is not in eV.
    """
    _check_ev(ref, target)

    if signed:
        c_ref, _ = _dominant_lobe_centroid(ref.x, ref.y)
        c_tar, _ = _dominant_lobe_centroid(target.x, target.y)
    else:
        c_ref = float(ref.x[np.argmax(np.abs(ref.y))])
        c_tar = float(target.x[np.argmax(np.abs(target.y))])

    shift  = c_ref - c_tar
    x_grid = _uniform_grid(ref.x, target.x + shift, n_points)
    y1     = _interpolate(ref.x, ref.y, x_grid)
    y2     = _interpolate(target.x + shift, target.y, x_grid)

    overlap = _lobe_overlaps(x_grid, y1, y2) if signed else _cosine(x_grid, y1, y2)
    return shift, overlap


def find_best_shift(
    ref: Spectrum,
    target: Spectrum,
    shift_range: np.ndarray = np.arange(-0.5, 0.51, 0.01),
    n_points: int = 1000,
    signed: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """Find the shift maximising spectral overlap by grid search.

    For signed spectra, maximisation is over the mean of (o_pos + o_neg) / 2,
    i.e. the shift that best aligns both lobes simultaneously.

    The default shift_range of ±0.5 eV covers the typical TD-DFT systematic
    error for organic chromophores. Adjust for larger errors.

    Args:
        ref (Spectrum): Reference spectrum, xunit='ev'.
        target (Spectrum): Target spectrum, xunit='ev'.
        shift_range (np.ndarray): Shifts to evaluate in eV.
        n_points (int): Number of interpolation grid points.
        signed (bool): If True, optimise mean lobe overlap.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (shifts, overlaps), same length as
            shift_range. For signed, overlaps is the mean (o_pos+o_neg)/2.

    Raises:
        ValueError: If either spectrum is not in eV.
    """
    _check_ev(ref, target)
    x_grid = _uniform_grid(
        ref.x, target.x, n_points,
        shift_min=float(shift_range.min()),
        shift_max=float(shift_range.max()),
    )
    y_ref = _interpolate(ref.x, ref.y, x_grid)

    overlaps = np.empty(len(shift_range))
    for i, shift in enumerate(shift_range):
        y_shifted = _interpolate(target.x + shift, target.y, x_grid)
        if signed:
            o_pos, o_neg = _lobe_overlaps(x_grid, y_ref, y_shifted)
            overlaps[i] = (o_pos + o_neg) / 2.0
        else:
            overlaps[i] = _cosine(x_grid, y_ref, y_shifted)

    return np.array(shift_range), overlaps


def main_band_sign(spec: Spectrum) -> int:
    """Sign of the dominant lobe of a signed spectrum.

    Dominant lobe is the one with the larger absolute integrated area.
    For a purely positive spectrum (LUM) this always returns +1.

    Args:
        spec (Spectrum): Input spectrum.

    Returns:
        int: +1 or -1.
    """
    _, sign = _dominant_lobe_centroid(spec.x, spec.y)
    return sign


def signs_match(ref: Spectrum, target: Spectrum) -> bool:
    """Return True if ref and target share the same dominant lobe sign.

    The primary qualitative criterion for a modelled CPL spectrum: does
    the model reproduce the correct chiroptical response direction?

    Args:
        ref (Spectrum): Reference spectrum.
        target (Spectrum): Target spectrum.

    Returns:
        bool: True if dominant lobe signs agree.
    """
    return main_band_sign(ref) == main_band_sign(target)


def benchmark_summary(
    ref: Spectrum,
    target: Spectrum,
    shift_range: np.ndarray = np.arange(-0.5, 0.51, 0.01),
    n_points: int = 1000,
    signed: bool = True,
) -> dict:
    """Full set of benchmarking metrics comparing a modelled spectrum to experiment.

    Metrics:
        signs_match (bool):
            Qualitative pass/fail — correct CPL response direction.
        overlap_pos (float):
            Cosine similarity of positive lobes (signed) or full cosine (unsigned).
        overlap_neg (float | None):
            Cosine similarity of negative lobes. None for unsigned.
        best_shift (float):
            Shift in eV maximising overlap. Encodes systematic energy error.
        best_overlap (float):
            Mean lobe overlap at best_shift (signed) or cosine (unsigned).

    Args:
        ref (Spectrum): Reference (experimental) spectrum, xunit='ev'.
        target (Spectrum): Target (modelled) spectrum, xunit='ev'.
        shift_range (np.ndarray): Shift grid in eV.
        n_points (int): Interpolation grid points.
        signed (bool): Use lobe overlap. True for CPL, False for LUM.

    Returns:
        dict: Metric names to values.

    Raises:
        ValueError: If either spectrum is not in eV.
    """
    _check_ev(ref, target)

    shifts, overlaps = find_best_shift(
        ref, target,
        shift_range=shift_range,
        n_points=n_points,
        signed=signed,
    )
    best_idx = int(np.argmax(overlaps))

    if signed:
        o_pos, o_neg = compute_overlap(ref, target, n_points=n_points, signed=True)
        return {
            "signs_match" : signs_match(ref, target),
            "overlap_pos" : o_pos,
            "overlap_neg" : o_neg,
            "best_shift"  : float(shifts[best_idx]),
            "best_overlap": float(overlaps[best_idx]),
        }
    else:
        return {
            "signs_match" : None,
            "overlap_pos" : float(compute_overlap(ref, target, n_points=n_points, signed=False)),
            "overlap_neg" : None,
            "best_shift"  : float(shifts[best_idx]),
            "best_overlap": float(overlaps[best_idx]),
        }


def broaden_sticks(
    energies: np.ndarray,
    strengths: np.ndarray,
    x_grid: np.ndarray,
    sigma: float = 0.1,
) -> Spectrum:
    """Broaden a stick spectrum into a continuous lineshape via Gaussian convolution.

    Suitable for both unsigned (oscillator strengths) and signed (rotatory
    strengths, CPL) stick spectra from quantum chemistry output.

    Args:
        energies (np.ndarray): Excitation energies in eV.
        strengths (np.ndarray): Stick intensities (signed or unsigned).
        x_grid (np.ndarray): Energy grid in eV, must be strictly increasing.
        sigma (float): Gaussian broadening width in eV. Typical values:
            0.05–0.10 eV for gas phase, 0.10–0.20 eV for solution.

    Returns:
        Spectrum: Broadened spectrum on x_grid with xunit='ev'.
    """
    y = np.zeros_like(x_grid, dtype=float)
    for e, s in zip(energies, strengths):
        y += s * np.exp(-0.5 * ((x_grid - e) / sigma) ** 2)
    return Spectrum(x=x_grid, y=y, xunit="ev")


def plot_shift_series(
    ref: Spectrum,
    target: Spectrum,
    shifts: list[float],
    n_points: int = 1000,
    filename: Optional[str] = None,
) -> None:
    """Plot reference alongside several shifted target spectra.

    Args:
        ref (Spectrum): Reference spectrum, xunit='ev'.
        target (Spectrum): Target spectrum, xunit='ev'.
        shifts (list[float]): Shifts in eV to apply to target.
        n_points (int): Number of interpolation grid points.
        filename (Optional[str]): Save to this path if given, else display.

    Raises:
        ValueError: If either spectrum is not in eV.
    """
    import matplotlib.pyplot as plt

    _check_ev(ref, target)
    x_grid = _uniform_grid(ref.x, target.x, n_points)
    y_ref  = _interpolate(ref.x, ref.y, x_grid)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x_grid, y_ref, label="Reference", linewidth=2, color="black")
    for shift in shifts:
        y_shifted = _interpolate(target.x + shift, target.y, x_grid)
        ax.plot(x_grid, y_shifted, linestyle="--", label=f"shift={shift:+.3f} eV")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle=":")
    ax.set_xlabel("Energy (eV)")
    ax.set_ylabel("Intensity")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if filename:
        fig.savefig(filename, dpi=150)
        plt.close(fig)
    else:
        plt.show()