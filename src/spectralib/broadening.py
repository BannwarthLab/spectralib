"""Broadening of stick spectra.

All line shapes are area-normalised and parametrised by their FWHM, in the units of
the energy grid. Stick energies, grid and FWHM must share one linear energy unit
('ev' or 'cm-1'); broadening on a wavelength grid is not supported (convert afterwards).

"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from unitkit import convert_energy_unit

from spectralib.spectrum import Spectrum
from spectralib.units import CGS40, K_DEPS, K_EPS, K_EPS_D

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


def ensemble_sticks(frames: Iterable[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    """Pool the sticks of N snapshots/conformers with equal weight 1/N.

    Args:
        frames: Iterable of (energies, strengths) per snapshot.

    Returns:
        (energies, strengths) of the pooled stick spectrum.
    """
    frames = list(frames)
    if not frames:
        raise ValueError("No frames given.")
    e = np.concatenate([np.atleast_1d(f[0]) for f in frames]).astype(float)
    s = np.concatenate([np.atleast_1d(f[1]) for f in frames]).astype(float) / len(frames)
    return e, s


def _to_cm1(energies: np.ndarray, grid: np.ndarray, fwhm: float, unit: str) -> tuple:
    if unit not in ("ev", "cm-1"):
        raise ValueError("unit must be 'ev' or 'cm-1'")
    fac = convert_energy_unit(1.0, unit, "cm-1")  # linear, so widths scale the same way
    return np.asarray(energies, dtype=float) * fac, np.asarray(grid, dtype=float) * fac, fwhm * fac


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


def epsilon_spectrum(
    energies: np.ndarray,
    f: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """Molar decadic absorption coefficient eps in L mol^-1 cm^-1.

    eps(nu) = K_EPS * sum_i f_i g(nu - nu_i), g normalised in cm^-1, K_EPS = 2.315e8 L mol^-1 cm^-2.
    energies/grid/fwhm in ``unit`` ('ev' or 'cm-1'); the returned spectrum keeps that unit.
    """
    e, x, w = _to_cm1(energies, grid, fwhm, unit)
    return Spectrum(grid, K_EPS * broaden(e, f, x, w, shape), xunit=unit)


def delta_epsilon_spectrum(
    energies: np.ndarray,
    r: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """ECD as delta-eps in L mol^-1 cm^-1 from rotatory strengths R in 1e-40 esu^2 cm^2.

    ::

        delta_eps(nu) = 32 pi^3 N_A nu / (3000 ln10 h c) * sum_i R_i g(nu - nu_i)  (cgs, nu in cm^-1)
                      = nu * sum_i R_i[1e-40 cgs] g(nu - nu_i) / 22.96

    Same construction as eps written with dipole strengths, so delta_eps/eps -> 4R/D = g_abs.
    """
    e, x, w = _to_cm1(energies, grid, fwhm, unit)
    return Spectrum(grid, K_DEPS * CGS40 * x * broaden(e, r, x, w, shape), xunit=unit)


def epsilon_spectrum_from_d(
    energies: np.ndarray,
    d: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """eps from dipole strengths D in 1e-40 esu^2 cm^2 (nu-weighted on the grid, like delta_eps).

    Use together with delta_epsilon_spectrum when the ratio delta_eps/eps (g_abs spectrum) is needed.
    """
    e, x, w = _to_cm1(energies, grid, fwhm, unit)
    return Spectrum(grid, K_EPS_D * CGS40 * x * broaden(e, d, x, w, shape), xunit=unit)


def emission_spectrum(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: float,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """Photon-counting emission profile, arbitrary units: y(E) = E^3 * sum_i s_i g(E - E_i).

    strengths = D_i for luminescence, 4 R_i for CPL (delta I), both in the same units, so that
    delta I / I -> g_lum. The E^3 factor is the spontaneous-emission density of states
    (photon counts; energy flux would be E^4). Compare with experimental spectra converted to
    energy with Spectrum.convert_x(..., jacobian=True).
    """
    x = np.asarray(grid, dtype=float)
    return Spectrum(grid, x**3 * broaden(energies, strengths, x, fwhm, shape), xunit=unit)
