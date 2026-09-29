"""Parser for ORCA TDDFT/TDA transition tables."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from cpl50.units import convert_x

_TABLES = {
    "f_len": "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS",
    "f_vel": "ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS",
    "r_len": "CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS",
    "r_vel": "CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS",
}
# ORCA >= 6:  "  0-1A  ->  1-1A    3.396117   27391.5   365.1   0.002364012 ..."
_ROW6 = re.compile(r"^\s*\S+\s+->\s+(\S+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.Ee+]+)")
# ORCA 5:     "     1   27391.5    365.1   0.002364012 ..."
_ROW5 = re.compile(r"^\s*(\d+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.Ee+]+)")
_MAX_HEADER = 8  # lines of dashes/column titles between table title and first row


def _parse_table(lines: list[str], start: int) -> tuple[np.ndarray, np.ndarray]:
    """Energies (eV) and value column of the table whose title is at lines[start]."""
    ev, val = [], []
    for k, line in enumerate(lines[start + 1 :]):
        if not ev and k > _MAX_HEADER:
            break  # empty table
        if m := _ROW6.match(line):
            ev.append(float(m.group(2)))
            val.append(float(m.group(5)))
        elif m := _ROW5.match(line):
            ev.append(float(convert_x(float(m.group(2)), "cm-1", "ev")))
            val.append(float(m.group(4)))
        elif ev:
            break  # end of table; lines before the first row are headers/dashes
    return np.array(ev), np.array(val)


def read_orca_tddft(filename: str | Path) -> dict[str, np.ndarray]:
    """Read the transition tables of the *last* TDDFT block in an ORCA output.

    Returns:
        dict with 'energy' (eV) and whichever of 'f_len', 'f_vel' (oscillator strengths)
        and 'r_len', 'r_vel' (rotatory strengths, 1e-40 esu^2 cm^2) are present.

    Raises:
        ValueError: If no absorption table is found or tables disagree in length/energies.
    """
    lines = Path(filename).read_text().splitlines()
    out: dict[str, np.ndarray] = {}
    for key, title in _TABLES.items():
        starts = [i for i, line in enumerate(lines) if title in line]
        if not starts:
            continue
        energy, values = _parse_table(lines, starts[-1])
        if "energy" in out and not np.allclose(out["energy"], energy, atol=1e-5):
            raise ValueError(f"Inconsistent transition energies in table '{key}' of {filename}")
        out.setdefault("energy", energy)
        out[key] = values
    if "f_len" not in out:
        raise ValueError(f"No TDDFT absorption table found in {filename}")
    return out
