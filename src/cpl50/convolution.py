""" Helper functions to broaden stick spectra via Gaussian convolution. """

from __future__ import annotations

import numpy as np

from cpl50.utils import Spectrum


def gaussian_profile(
    center: float,
    sigma: float,
    x: np.ndarray,
) -> np.ndarray:
    """
    Compute normalized Gaussian distribution.

    Args:
        center: Center of the Gaussian (x_0).
        sigma: Standard deviation (not FWHM; for FWHM use sigma = FWHM / 2.355).
        x: Array of x values.

    Returns:
        Normalized Gaussian values at each x.
    """
    return (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - center) / sigma) ** 2)


def broaden_spectrum(
    energies: np.ndarray,
    strengths: np.ndarray,
    e_min: float = 0.0,
    e_max: float = 6.0,
    sigma: float = 0.1,
    n_points: int = 1000,
) -> Spectrum:
    """
    Broaden stick spectrum via Gaussian convolution (convenience wrapper).

    Args:
        energies: Excitation energies in eV.
        strengths: Stick intensities (oscillator or rotatory strengths).
        e_min: Minimum energy in eV.
        e_max: Maximum energy in eV.
        sigma: Standard deviation of Gaussian in eV.
        n_points: Number of grid points.

    Returns:
        Spectrum: Broadened spectrum with xunit='ev'.
    """
    x_grid = np.linspace(e_min, e_max, n_points)
    y = np.zeros_like(x_grid, dtype=float)

    for e, s in zip(energies, strengths):
        y += s * gaussian_profile(e, sigma, x_grid)

    return Spectrum(x=x_grid, y=y, xunit="ev")




