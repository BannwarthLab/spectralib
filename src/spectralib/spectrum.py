"""Spectrum container: x/y arrays with an explicit x unit and header metadata."""

from __future__ import annotations

import numpy as np
from scipy.integrate import trapezoid
from unitkit import convert_energy_unit

#: Energy-axis units (unitkit spelling).
X_UNITS = ("nm", "ev", "cm-1")


def _jacobian(x: np.ndarray, init: str, final: str) -> np.ndarray:
    r""":math:`|dx_\mathrm{init}/dx_\mathrm{final}|` at x (init units) up to a constant.

    x^2 for nm -> energy, x^-2 for energy -> nm.
    """
    if (init == "nm") == (final == "nm"):
        return np.ones_like(x)
    return x**2 if init == "nm" else 1.0 / x**2


class Spectrum:
    """Immutable-by-convention spectrum; every transformation returns a new instance.

    Args:
        x: Strictly increasing x values.
        y: y values, same shape as x.
        xunit: One of 'nm', 'ev', 'cm-1' (default 'nm' as in the dataset .csv files).
        metadata: Header fields (see spectralib.io.read_spectrum).
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, xunit: str = "nm", metadata: dict | None = None) -> None:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x.shape != y.shape:
            raise ValueError(f"x and y must have the same shape, got {x.shape} vs {y.shape}")
        if not np.all(np.diff(x) > 0):
            raise ValueError("x must be strictly increasing.")
        xunit = xunit.lower()
        if xunit not in X_UNITS:
            raise ValueError(f"Unknown xunit '{xunit}'. Choose from {X_UNITS}.")
        self.x, self.y, self.xunit = x, y, xunit
        self.metadata = dict(metadata or {})

    def _new(self, x: np.ndarray, y: np.ndarray, xunit: str | None = None) -> Spectrum:
        return Spectrum(x, y, xunit or self.xunit, self.metadata)

    def convert_x(self, final: str, jacobian: bool = False) -> Spectrum:
        r"""Convert the x axis; reorders points for reciprocal conversions (nm <-> energy).

        Args:
            final: Target unit.
            jacobian: Multiply y by :math:`|dx_\mathrm{old}/dx_\mathrm{new}|` (up to a constant). Use for spectral
                densities recorded per wavelength interval (LUM intensity, CPL delta I);
                not for epsilon, delta-epsilon or g_lum.
        """
        final = final.lower()
        if final not in X_UNITS:
            raise ValueError(f"Unknown xunit '{final}'. Choose from {X_UNITS}.")
        # copy: convert_energy_unit overwrites arrays in place for nm <-> energy
        x_new = np.asarray(convert_energy_unit(self.x.copy(), self.xunit, final))
        y_new = self.y * _jacobian(self.x, self.xunit, final) if jacobian else self.y.copy()
        order = np.argsort(x_new)
        return self._new(x_new[order], y_new[order], final)

    def scale_y(self, factor: float) -> Spectrum:
        return self._new(self.x, self.y * factor)

    def shift_x(self, shift: float) -> Spectrum:
        """Rigid shift of the x axis (meaningful on energy axes)."""
        return self._new(self.x + shift, self.y)

    def crop(self, xmin: float = -np.inf, xmax: float = np.inf) -> Spectrum:
        mask = (self.x >= xmin) & (self.x <= xmax)
        return self._new(self.x[mask], self.y[mask])

    def normalize(self, mode: str = "max") -> Spectrum:
        r"""Sign-preserving normalisation.

        - ``mode='max'``: :math:`\max|y| = 1` (plotting; depends on broadening width).
        - ``mode='area'``: :math:`\int|y|\,dx = 1` (metrics; invariant to broadening width for isolated bands).
        """
        if mode == "max":
            norm = np.max(np.abs(self.y))
        elif mode == "area":
            norm = trapezoid(np.abs(self.y), self.x)
        else:
            raise ValueError("mode must be 'max' or 'area'")
        if norm == 0:
            raise ValueError("Cannot normalise a zero spectrum.")
        return self.scale_y(1.0 / norm)

    def __call__(self, x_new: np.ndarray) -> np.ndarray:
        """Linear interpolation onto x_new, zero outside the data range."""
        return np.interp(x_new, self.x, self.y, left=0.0, right=0.0)

    def __len__(self) -> int:
        return len(self.x)

    def __repr__(self) -> str:
        mol = self.metadata.get("molname", "")
        tag = f"mol={mol}, " if mol else ""
        return f"Spectrum({tag}n={len(self)}, x=[{self.x[0]:.4f}, {self.x[-1]:.4f}] {self.xunit})"
