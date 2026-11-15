"""Broadening of stick spectra.

All line shapes are area-normalised and parametrised by their FWHM, in the units of
the energy grid. Stick energies, grid and FWHM must share one linear energy unit
('ev' or 'cm-1'); broadening on a wavelength grid is not supported (convert afterwards).

"""

from __future__ import annotations

import numpy as np

from spectralib.spectrum import Spectrum

_FWHM_PER_SIGMA = 2.0 * np.sqrt(2.0 * np.log(2.0))


def fwhm_from_sigma(sigma: float) -> float:
    """FWHM of a Gaussian from its standard deviation (FWHM = 2 sqrt(2 ln 2) sigma)."""
    return sigma * _FWHM_PER_SIGMA


def sigma_from_fwhm(fwhm: float) -> float:
    """Standard deviation of a Gaussian from its FWHM (inverse of :func:`fwhm_from_sigma`)."""
    return fwhm / _FWHM_PER_SIGMA


def fwhm_from_fw1e(fw1e: float) -> float:
    """FWHM from the full width at 1/e of the maximum (FWHM = sqrt(ln 2) * FW1/e)."""
    return fw1e * np.sqrt(np.log(2.0))


def gaussian(x: np.ndarray, center: float | np.ndarray, fwhm: float) -> np.ndarray:
    sigma = fwhm / _FWHM_PER_SIGMA
    return np.exp(-0.5 * ((x - center) / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))


def lorentzian(x: np.ndarray, center: float | np.ndarray, fwhm: float) -> np.ndarray:
    hwhm = fwhm / 2.0
    return hwhm / (np.pi * ((x - center) ** 2 + hwhm**2))


_SHAPES = {"gaussian": gaussian, "lorentzian": lorentzian}


def broaden(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    shape: str = "gaussian",
) -> np.ndarray:
    """sum_i s_i * g(grid - E_i), g area-normalised (so integral = sum_i s_i on a wide grid)."""
    e = np.atleast_1d(np.asarray(energies, dtype=float))[:, None]
    s = np.atleast_1d(np.asarray(strengths, dtype=float))
    return s @ _SHAPES[shape](np.asarray(grid, dtype=float)[None, :], e, fwhm)


def spectrum(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """Broadened spectrum in arbitrary units (y = broaden(...))."""
    return Spectrum(grid, broaden(energies, strengths, grid, fwhm, shape), xunit=unit)


def emission_spectrum(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    r"""Photon-counting emission profile in arbitrary units, :math:`y(E) = E^3 \sum_i s_i\, g(E - E_i)`.

    ``strengths`` are dipole strengths :math:`D_i = |\mu_{0i}|^2` for the total intensity
    :math:`I = I_\mathrm{L} + I_\mathrm{R}` (luminescence) and :math:`2R_i` for
    :math:`\Delta I = I_\mathrm{L} - I_\mathrm{R}` (CPL). With D and R in the same units,
    :math:`g_\mathrm{lum} = 2\Delta I/I = 4R/D`. From an oscillator strength,
    :math:`D_i = 3 f_i / (2 E_i)` in atomic units (:math:`E_h`, :math:`e^2 a_0^2`), and
    :math:`1\,e^2 a_0^2 = 64604.75 \times 10^{-40}` esu\ :sup:`2` cm\ :sup:`2`, the usual unit of R.
    The :math:`E^3` factor is the density of states of spontaneous emission (photon counts per energy
    interval; an energy flux would scale with :math:`E^4`). Compare with experimental spectra converted
    with ``Spectrum.convert_x("ev", jacobian=True)``.
    """
    x = np.asarray(grid, dtype=float)
    return Spectrum(grid, x**3 * broaden(energies, strengths, x, fwhm, shape), xunit=unit)
