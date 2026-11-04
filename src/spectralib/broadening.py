"""Broadening of stick spectra.

All line shapes are area-normalised and parametrised by their FWHM, in the units of
the energy grid. Stick energies, grid and FWHM must share one linear energy unit
('ev' or 'cm-1'); broadening on a wavelength grid is not supported (convert afterwards).

Available shapes (``shape=`` argument, ``fwhm=`` value):

* ``"gaussian"``, ``"lorentzian"``: one FWHM.
* ``"voigt"``: exact Voigt profile (Gaussian convolved with Lorentzian, Faddeeva function),
  ``fwhm=(fwhm_gauss, fwhm_lorentz)``.
* ``"pseudo_voigt"``: Thompson-Cox-Hastings pseudo-Voigt
  (weighted sum of a Gaussian and a Lorentzian of the same total FWHM), same ``fwhm`` tuple.
  Within ~1.5 % of the exact Voigt (relative to the peak height), cheaper to evaluate.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence

import numpy as np
from scipy.special import wofz
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


def voigt_fwhm(fwhm_gauss: float, fwhm_lorentz: float) -> float:
    """FWHM of the Voigt profile from its Gaussian and Lorentzian FWHMs.

    Olivero-Longbotham approximation :cite:`oliveroEmpiricalFitsVoigt1977`
    f = 0.5346 f_L + sqrt(0.2166 f_L^2 + f_G^2), within 0.03 % of the exact Voigt FWHM.
    """
    return float(0.5346 * fwhm_lorentz + np.sqrt(0.2166 * fwhm_lorentz**2 + fwhm_gauss**2))


def _tch_fwhm(fwhm_gauss: float, fwhm_lorentz: float) -> float:
    """Total FWHM of the TCH pseudo-Voigt.

    Up to 0.5 % off the exact Voigt FWHM, but the TCH mixing parameter eta is fitted with this width.
    """
    g, lo = fwhm_gauss, fwhm_lorentz
    return float(
        (g**5 + 2.69269 * g**4 * lo + 2.42843 * g**3 * lo**2 + 4.47163 * g**2 * lo**3 + 0.07842 * g * lo**4 + lo**5)
        ** 0.2
    )


def _check_voigt_widths(fwhm_gauss: float, fwhm_lorentz: float) -> None:
    if fwhm_gauss < 0 or fwhm_lorentz < 0 or fwhm_gauss + fwhm_lorentz == 0:
        raise ValueError("Voigt widths must be >= 0 and not both zero.")


def voigt(x: np.ndarray, center: float | np.ndarray, fwhm_gauss: float, fwhm_lorentz: float) -> np.ndarray:
    """Exact, area-normalised Voigt profile: Re w(z) / (sigma sqrt(2 pi)), z = (x - x0 + i gamma) / (sigma sqrt 2).

    w is the Faddeeva function, sigma the Gaussian standard deviation and gamma = fwhm_lorentz / 2.
    A zero width reduces to the pure :func:`gaussian` or :func:`lorentzian`.
    """
    _check_voigt_widths(fwhm_gauss, fwhm_lorentz)
    if fwhm_gauss == 0:
        return lorentzian(x, center, fwhm_lorentz)
    if fwhm_lorentz == 0:
        return gaussian(x, center, fwhm_gauss)
    sigma = sigma_from_fwhm(fwhm_gauss)
    z = ((x - center) + 0.5j * fwhm_lorentz) / (sigma * np.sqrt(2.0))
    return np.real(wofz(z)) / (sigma * np.sqrt(2.0 * np.pi))


def pseudo_voigt_eta(fwhm_gauss: float, fwhm_lorentz: float) -> float:
    """Lorentzian fraction eta of the TCH pseudo-Voigt :cite:`thompsonRietveldRefinementDebye1987`."""
    q = fwhm_lorentz / _tch_fwhm(fwhm_gauss, fwhm_lorentz)
    return float(np.clip(1.36603 * q - 0.47719 * q**2 + 0.11116 * q**3, 0.0, 1.0))


def pseudo_voigt(x: np.ndarray, center: float | np.ndarray, fwhm_gauss: float, fwhm_lorentz: float) -> np.ndarray:
    """Thompson-Cox-Hastings pseudo-Voigt, area-normalised.

    eta * L(x; f) + (1 - eta) * G(x; f): both components share one total FWHM f (TCH polynomial),
    eta from :func:`pseudo_voigt_eta`. Deviates from the exact :func:`voigt` by at most ~1.5 % of the peak height.
    """
    _check_voigt_widths(fwhm_gauss, fwhm_lorentz)
    f = _tch_fwhm(fwhm_gauss, fwhm_lorentz)
    eta = pseudo_voigt_eta(fwhm_gauss, fwhm_lorentz)
    return eta * lorentzian(x, center, f) + (1.0 - eta) * gaussian(x, center, f)


# name -> (line shape, number of FWHM parameters)
_SHAPES: dict[str, tuple[Callable[..., np.ndarray], int]] = {
    "gaussian": (gaussian, 1),
    "lorentzian": (lorentzian, 1),
    "voigt": (voigt, 2),
    "pseudo_voigt": (pseudo_voigt, 2),
}

Width = float | Sequence[float]
"""One FWHM, or ``(fwhm_gauss, fwhm_lorentz)`` for ``"voigt"`` / ``"pseudo_voigt"``."""


def _lineshape(shape: str, fwhm: Width) -> tuple[Callable[..., np.ndarray], tuple[float, ...]]:
    if shape not in _SHAPES:
        raise ValueError(f"Unknown shape {shape!r}, choose from {sorted(_SHAPES)}.")
    func, n = _SHAPES[shape]
    widths = tuple(float(w) for w in np.atleast_1d(np.asarray(fwhm, dtype=float)))
    if len(widths) != n:
        raise ValueError(f"shape {shape!r} needs {n} FWHM value(s), got {len(widths)}.")
    return func, widths


def broaden(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: Width,
    shape: str = "gaussian",
) -> np.ndarray:
    """sum_i s_i * g(grid - E_i), g area-normalised (so integral = sum_i s_i on a wide grid).

    ``fwhm`` is one width, or ``(fwhm_gauss, fwhm_lorentz)`` for ``shape="voigt"`` / ``"pseudo_voigt"``.
    """
    func, widths = _lineshape(shape, fwhm)
    e = np.atleast_1d(np.asarray(energies, dtype=float))[:, None]
    s = np.atleast_1d(np.asarray(strengths, dtype=float))
    return s @ func(np.asarray(grid, dtype=float)[None, :], e, *widths)


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


def _to_cm1(energies: np.ndarray, grid: np.ndarray, fwhm: Width, unit: str) -> tuple:
    if unit not in ("ev", "cm-1"):
        raise ValueError("unit must be 'ev' or 'cm-1'")
    fac = convert_energy_unit(1.0, unit, "cm-1")  # linear, so widths scale the same way
    w = np.asarray(fwhm, dtype=float) * fac
    return np.asarray(energies, dtype=float) * fac, np.asarray(grid, dtype=float) * fac, tuple(np.atleast_1d(w))


def spectrum(
    energies: np.ndarray,
    strengths: np.ndarray,
    grid: np.ndarray,
    fwhm: Width,
    unit: str = "ev",
    shape: str = "gaussian",
) -> Spectrum:
    """Broadened spectrum in arbitrary units (y = broaden(...))."""
    return Spectrum(grid, broaden(energies, strengths, grid, fwhm, shape), xunit=unit)


def epsilon_spectrum(
    energies: np.ndarray,
    f: np.ndarray,
    grid: np.ndarray,
    fwhm: Width,
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
    fwhm: Width,
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
    fwhm: Width,
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
    fwhm: Width,
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
