"""Matplotlib helpers (optional dependency: pip install cpl50[plot])."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from cpl50.spectrum import Spectrum
from cpl50.units import convert_x

_XLABEL = {"ev": "Energy / eV", "cm-1": r"Wavenumber / cm$^{-1}$", "nm": "Wavelength / nm"}


def _ax(ax: plt.Axes | None) -> plt.Axes:
    return ax if ax is not None else plt.subplots(figsize=(6, 4))[1]


def plot_spectrum(spec: Spectrum, ax: plt.Axes | None = None, **kwargs) -> plt.Axes:
    ax = _ax(ax)
    ax.plot(spec.x, spec.y, lw=kwargs.pop("lw", 2), **kwargs)
    ax.set_xlabel(_XLABEL[spec.xunit])
    return ax


def plot_sticks(
    energies: np.ndarray, strengths: np.ndarray, ax: plt.Axes | None = None, scale: float = 1.0, **kwargs
) -> plt.Axes:
    ax = _ax(ax)
    ax.vlines(energies, 0.0, np.asarray(strengths) * scale, lw=kwargs.pop("lw", 1), **kwargs)
    return ax


def add_wavelength_axis(ax: plt.Axes) -> plt.Axes:
    """Secondary top axis in nm for an eV bottom axis."""

    def f(x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        out = np.full_like(x, np.inf)
        ok = x > 0
        out[ok] = convert_x(x[ok], "ev", "nm")
        return out

    sec = ax.secondary_xaxis("top", functions=(f, f))
    sec.set_xlabel(_XLABEL["nm"])
    return sec


def plot_comparison(
    ref: Spectrum,
    calc: Spectrum,
    shift: float = 0.0,
    norm: str = "max",
    ax: plt.Axes | None = None,
    labels: tuple[str, str] = ("Experiment", "Calculated"),
) -> plt.Axes:
    """Reference and shifted calculated spectrum, both normalised (sign-preserving)."""
    ax = _ax(ax)
    plot_spectrum(ref.normalize(norm), ax, color="#1f1f1f", label=labels[0])
    lbl = labels[1] + (f" ({shift:+.2f} eV)" if shift else "")
    visible = calc.shift_x(shift).crop(ref.x[0], ref.x[-1])  # normalise within the measured window
    plot_spectrum(visible.normalize(norm), ax, color="#2a6fdb", label=lbl)
    ax.axhline(0.0, color="0.6", lw=0.8)
    ax.set_xlim(ref.x[0], ref.x[-1])
    ax.set_ylabel("Normalised intensity")
    ax.legend(frameon=False)
    return ax
