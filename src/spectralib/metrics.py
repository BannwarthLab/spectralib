"""Comparison metrics between a reference (usually experimental) and a calculated spectrum."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from scipy.integrate import trapezoid

from spectralib.broadening import gaussian
from spectralib.spectrum import Spectrum

_N = 2000


# ----------------------------------------------------------------------------- helpers


def _check_ev(*spectra: Spectrum) -> None:
    for s in spectra:
        if s.xunit != "ev":
            raise ValueError(f"Spectrum must be in eV (got '{s.xunit}'); use spec.convert_x('ev').")


def _grid(ref: Spectrum, calc: Spectrum, shifts: np.ndarray, n: int, window: str) -> np.ndarray:
    if window == "ref":
        lo, hi = ref.x[0], ref.x[-1]
    elif window == "union":
        lo = min(ref.x[0], calc.x[0] + shifts.min())
        hi = max(ref.x[-1], calc.x[-1] + shifts.max())
    else:
        raise ValueError("window must be 'ref' or 'union'")
    return np.linspace(lo, hi, n)


def _sample(ref: Spectrum, calc: Spectrum, shifts: npt.ArrayLike, n: int, window: str) -> tuple:
    """x (n,), a = ref (n,), b = calc(x - shift) (m, n) for every shift."""
    _check_ev(ref, calc)
    s = np.atleast_1d(np.asarray(shifts, dtype=float))
    x = _grid(ref, calc, s, n, window)
    return x, ref(x), calc(x[None, :] - s[:, None])


def _cos(x: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """int a b / sqrt(int a^2 int b^2) along the last axis; nan where a norm vanishes."""
    num = trapezoid(a * b, x, axis=-1)
    den = np.sqrt(trapezoid(a * a, x, axis=-1) * trapezoid(b * b, x, axis=-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def _lobes(x: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Cosines of positive parts and of negative parts.

    nan if the lobe is absent in both spectra (lobe not applicable), 0 if absent in one.
    """
    out = []
    for pa, pb in ((np.maximum(a, 0), np.maximum(b, 0)), (np.maximum(-a, 0), np.maximum(-b, 0))):
        c = _cos(x, pa, pb)
        has_a = np.broadcast_to(np.any(pa > 0, axis=-1), np.shape(c))
        has_b = np.any(pb > 0, axis=-1)
        out.append(np.where(has_a | has_b, np.nan_to_num(c, nan=0.0), np.nan))
    return out[0], out[1]


def _objective(x: np.ndarray, a: np.ndarray, b: np.ndarray, kind: str) -> np.ndarray:
    if kind == "cosine":
        return _cos(x, a, b)
    if kind == "abs_cosine":
        return _cos(x, np.abs(a), np.abs(b))
    if kind == "lobes":
        return np.nanmean(np.vstack(_lobes(x, a, b)), axis=0)
    raise ValueError("objective must be 'cosine', 'abs_cosine' or 'lobes'")


# ----------------------------------------------------------------------------- shape metrics


def cosine(ref: Spectrum, calc: Spectrum, shift: float = 0.0, n: int = _N, window: str = "ref") -> float:
    """Signed cosine similarity in [-1, 1]; scale invariant. Enantiomer -> -1."""
    x, a, b = _sample(ref, calc, shift, n, window)
    return float(_cos(x, a, b[0]))


def lobe_cosines(
    ref: Spectrum, calc: Spectrum, shift: float = 0.0, n: int = _N, window: str = "ref"
) -> tuple[float, float]:
    """(o_pos, o_neg): cosine of positive lobes and of negative lobes separately.

    o is nan when that lobe exists in neither spectrum (e.g. o_neg for two positive CPL bands).
    """
    x, a, b = _sample(ref, calc, shift, n, window)
    o_pos, o_neg = _lobes(x, a, b[0])
    return float(o_pos), float(o_neg)


def optimal_shift(
    ref: Spectrum,
    calc: Spectrum,
    bounds: tuple[float, float] = (-1.0, 1.0),
    step: float = 0.005,
    objective: str = "cosine",
    n: int = _N,
    window: str = "ref",
) -> tuple[float, float]:
    """Shift of calc maximising ``objective`` by grid search + parabolic refinement.

    objective: 'cosine' (unsigned spectra), 'abs_cosine' (sign-agnostic alignment of signed
    spectra), 'lobes' (mean of applicable lobe cosines).

    Returns:
        (shift, objective value at the grid optimum).
    """
    shifts = np.arange(bounds[0], bounds[1] + 0.5 * step, step)
    x, a, b = _sample(ref, calc, shifts, n, window)
    vals = _objective(x, a, b, objective)
    if np.all(np.isnan(vals)):
        raise ValueError("Objective undefined for all shifts (no overlap).")
    i = int(np.nanargmax(vals))
    best = shifts[i]
    if 0 < i < len(shifts) - 1 and np.all(np.isfinite(vals[i - 1 : i + 2])):
        y0, y1, y2 = vals[i - 1 : i + 2]
        den = y0 - 2 * y1 + y2
        if den < 0:
            best += 0.5 * step * (y0 - y2) / den
    return float(best), float(vals[i])


# ----------------------------------------------------------------------------- sign / position


def lobe_areas(spec: Spectrum) -> tuple[float, float]:
    """(A+, A-) = integrals of the positive part and of the absolute value of the negative part."""
    return float(trapezoid(np.maximum(spec.y, 0), spec.x)), float(trapezoid(np.maximum(-spec.y, 0), spec.x))


def sign_ratio(spec: Spectrum) -> float:
    """(A+ - A-) / (A+ + A-) in [-1, 1]: +-1 for a single sign, ~0 if positive and negative lobes have similar areas (sign ill-defined)."""
    p, m = lobe_areas(spec)
    return (p - m) / (p + m) if p + m > 0 else 0.0


def dominant_sign(spec: Spectrum) -> int:
    """Sign of the lobe with the larger integrated area (+1 / -1)."""
    p, m = lobe_areas(spec)
    return 1 if p >= m else -1


def signs_match(ref: Spectrum, calc: Spectrum) -> bool:
    return dominant_sign(ref) == dominant_sign(calc)


def smooth(spec: Spectrum, fwhm: float) -> Spectrum:
    """Convolve with an area-normalised Gaussian of the given FWHM (x units); works on non-uniform x."""
    kern = gaussian(spec.x[:, None], spec.x[None, :], fwhm)
    y = trapezoid(kern * spec.y[None, :], spec.x, axis=1) / trapezoid(kern, spec.x, axis=1)
    return Spectrum(spec.x, y, spec.xunit, spec.metadata)


def peak_energy(spec: Spectrum, smooth_fwhm: float | None = None) -> float:
    """Position of the extremum of the dominant-sign lobe (optionally after Gaussian smoothing,
    recommended for noisy experimental CPL where the raw maximum is often a noise spike)."""
    s = smooth(spec, smooth_fwhm) if smooth_fwhm else spec
    return float(s.x[np.argmax(dominant_sign(s) * s.y)])


# ----------------------------------------------------------------------------- summary


def benchmark(
    ref: Spectrum,
    calc: Spectrum,
    signed: bool,
    shift: float | None = None,
    bounds: tuple[float, float] = (-1.0, 1.0),
    n: int = _N,
    window: str = "ref",
    smooth_fwhm: float | None = 0.05,
) -> dict:
    """All metrics for one reference/calculated pair.

    Protocol:
      1. peak_error = E_peak(calc) - E_peak(ref), before any shift; calc is restricted to the
         part that ``bounds`` can shift into the measured window, and the reference peak is
         taken after Gaussian smoothing (``smooth_fwhm``, eV; None to disable).
      2. shift: pass one explicitly (recommended for CPL/ECD: the shift found on the
         corresponding LUM/UV-vis pair, since both come from the same transitions), or it is
         optimised here - on :math:`|y|` for signed spectra, so the alignment cannot trade an energy
         error against a sign error.
      3. At that shift: signed cosine, lobe cosines (signed only).
      4. Signed: dominant-sign match (calc evaluated inside the window after the shift) plus
         sign ratios (a ref sign ratio near 0 means the main band sign is not well defined and
         the match should be read with care).
    """
    _check_ev(ref, calc)
    # sign / peak of calc only in the region that can be mapped onto the measured window
    visible = calc.crop(ref.x[0] - bounds[1], ref.x[-1] - bounds[0])
    out: dict = {"peak_error": peak_energy(visible) - peak_energy(ref, smooth_fwhm)}
    if shift is None:
        shift, _ = optimal_shift(ref, calc, bounds, objective="abs_cosine" if signed else "cosine", n=n, window=window)
    out["shift"] = float(shift)
    out["cosine"] = cosine(ref, calc, shift, n, window)
    if signed:
        out["o_pos"], out["o_neg"] = lobe_cosines(ref, calc, shift, n, window)
        in_window = calc.shift_x(shift).crop(ref.x[0], ref.x[-1])
        out["signs_match"] = signs_match(ref, in_window)
        out["sign_ratio_ref"] = sign_ratio(ref)
        out["sign_ratio_calc"] = sign_ratio(in_window)
    return out
