"""Utilities for computing spectral overlap and optimal energy shift."""

from __future__ import annotations

import numpy as np
from typing import List, Optional

from scipy.interpolate import interp1d
from scipy.integrate import trapezoid

from cpl50.utils import Spectrum

def _interpolate_spectrum(x: np.ndarray, y: np.ndarray, x_new: np.ndarray) -> np.ndarray:
    """ Interpolate spectrum on a uniform grid with cubic splines. 
    
        Args:
            x (np.ndarray): Init. datapoints in x.
            y (np.ndarray): Init. datapoints in y.
            x_new (np.ndarray): Grid to interpolate y on.

        Returns:
            y_new (np.ndarray): Interpolated y values on x_new.
    """
    f = interp1d(x, y, kind="cubic", bounds_error=False, fill_value=0.0)

    return f(x_new)


def _uniform_grid(x_ref: np.ndarray, x_tar: np.ndarray, n_points: int) -> np.ndarray:
    """Build a uniform grid from two sets of datapoints.
    
        Args:
            x_ref (np.ndarray): Datapoints of first spectrum,
            x_tar (np.ndarray): Datapts of second spectrum.
            n_points (np.ndarray): Number of points for interpol. 
        
        Returns:
            List of equidistant points spanning min/max of both spectra. 
    """
    x_min = min(np.min(x_ref), np.min(x_tar))
    x_max = max(np.max(x_ref), np.max(x_tar))
    return np.linspace(x_min, x_max, n_points)


def _normalize(x: np.ndarray, y: np.ndarray, mode: str = "area") -> float:
    """Compute different normalization factors for the computation of spectral overlap.
    
        Args:
            x, y (np.ndarray): datapts in x,y. 
            mode (str, opt): Overlap "mode" that depends normalization constant to be returned. Default: "area".
        
        Returns:
            normalization constant.
    """
    if mode == "area":
        return trapezoid(y, x)
    if mode == "cosine":
        return np.sqrt(trapezoid(y * y, x))
    if mode == "absolute":
        return trapezoid(np.abs(y), x)
    raise ValueError(f"Unknown overlap mode: {mode}")


def _evaluate_overlap(
    x: np.ndarray,
    y1: np.ndarray,
    y2: np.ndarray,
    mode: str = "area",
) -> float:
    """ Compute normalized overlap for two spectra interpolated on the same x grid. 
    
        Args:
            x (np.ndarray): Shared x datapts of the two y series.
            y1 (np.ndarray): Values of first function interpolated on x.
            y2 (np.ndarray): Values of second function interpolated on x.
            mode (str, opt): Expression used to compute overlap. Default: "area".
        Returns:
            
    """

    if mode == "absolute":
        overlap_raw = trapezoid(np.abs(y1 * y2), x)
    else:
        overlap_raw = trapezoid(y1 * y2, x)

    norm_ref = _normalize(y1, x, mode)
    norm_target = _normalize(y2, x, mode)

    if norm_ref == 0 or norm_target == 0:
        raise ValueError(
            "Overlap normalization factor is zero. "
            "Try a different overlap mode or verify the input spectra."
        )

    return overlap_raw / (norm_ref * norm_target)


def compute_overlap(
    ref: Spectrum,
    target: Spectrum,
    mode: str = "area",
    npts: int = 1000,
) -> float:
    """Compute overlap between two sets of spectra by interpolating them on a uniform grid.
    
        Args:
            ref (np.ndarray): Reference spectrum data.
            target (np.ndarray): Target spectrum data.
            mode (str, opt): Eq. to compute normalized overlap with. Default: "area".
            npts (int, opt): Number of points for interpolation. Default: 1000.

    """
    x_ref, y_ref = ref.x, ref.y

    x_tar, y_tar = target.x, target.y

    x_grid = _uniform_grid(x_ref, x_tar, npts)
    y_ref_interp = _interpolate_spectrum(x_ref, y_ref, x_grid)
    y_tar_interp = _interpolate_spectrum(x_tar, y_tar, x_grid)

    return _evaluate_overlap(y_ref_interp, y_tar_interp, x_grid, mode)


def find_best_shift(
    reference: Spectrum,
    target: Spectrum,
    shift_range: np.ndarray = np.arange(0, 1.1, 0.1),
    n_points: int = 1000,
    overlap_mode: str = "cosine",
) -> List[np.ndarray, np.ndarray]:
    """ Compute energetic shift that maximizes the spectral overlap between two spectra sets.

    Args:
        reference: Reference spectrum as a Spectrum dataclass.
        target: Target spectrum as a Spectrum dataclass.
        shift_range: Array of shifts to evaluate.
        n_points: Number of interpolation points on the uniform grid.
        overlap_mode: Overlap normalization mode.

    Returns:
        List of (shift, overlap) values for every evaluated shift.
    """

    x_ref, y_ref = reference.x, reference.y
    x_tar, y_tar = target.x, target.y

    shift_min = np.min(shift_range)
    shift_max = np.max(shift_range)
    x_grid = np.linspace(
        min(np.min(x_ref), np.min(x_tar) + shift_min),
        max(np.max(x_ref), np.max(x_tar) + shift_max),
        n_points,
    )
    y_ref_interp = _interpolate_spectrum(x_ref, y_ref, x_grid)

    shifts = []
    ovlps = []

    for shift in shift_range:
        y_shifted = _interpolate_spectrum(x_tar + shift, y_tar, x_grid)
        overlap = _evaluate_overlap(y_ref_interp, y_shifted, x_grid, overlap_mode)
        ovlps.append(overlap)
        shifts.append(shift)


    return [np.array(shifts), np.array(ovlps)]


def plot_shift_series(
    reference: Spectrum,
    target: Spectrum,
    shifts: List[float],
    n_points: int = 1000,
    filename: Optional[str] = None,
):
    """Plot reference spectrum with several shifted target spectra."""
    import matplotlib.pyplot as plt

    x_ref, y_ref = reference.x, reference.y
    x_tar, y_tar = target.x, target.y   

    x_grid = _uniform_grid(x_ref, x_tar, n_points)
    y_ref_interp = _interpolate_spectrum(x_ref, y_ref, x_grid)

    plt.figure(figsize=(10, 6))
    plt.plot(x_grid, y_ref_interp, label="Reference", linewidth=2)

    for shift in shifts:
        y_shifted = _interpolate_spectrum(x_tar + shift, y_tar, x_grid)
        plt.plot(x_grid, y_shifted, linestyle="--", label=f"Shift {shift:.2f}")

    plt.xlabel("Energy (eV)")
    plt.ylabel("Intensity")
    plt.legend()
    plt.grid(True)

    if filename:
        plt.savefig(filename, dpi=150)
        plt.close()
    else:
        plt.show()
