""" Contains parsers for ORCA output files. """

from __future__ import annotations

import re
from typing import Tuple, List


def read_absorption(filename: str) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Extract all absorption transition energies and oscillator strengths
    from an ORCA output file.

    Returns (E_eV, E_nm, osc_len, osc_vel) where:
        E_eV: transition energies in eV
        E_nm: transition wavelengths in nm
        osc_len: oscillator strengths (length dipole)
        osc_vel: oscillator strengths (velocity dipole)
    """
    e_ev = []
    e_nm = []
    f_len = []
    f_vel = []

    with open(filename, "r") as f:
        lines = f.readlines()

    # Extract from electric dipole (length) section
    in_section = False
    for i, line in enumerate(lines):
        if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
            in_section = True
            continue

        if in_section:
            stripped = line.strip()
            if stripped.startswith("-") or not stripped:
                if not stripped:
                    break
                continue

            parts = stripped.split()
            # Line format: "  0-1A  ->  1-1A    3.396117   27391.5   365.1   0.002364012   ..."
            if len(parts) >= 7 and "-" in parts[0] and "A" in parts[0]:
                try:
                    e_ev.append(float(parts[3]))      # Energy (eV)
                    e_nm.append(float(parts[5]))      # Wavelength (nm)
                    f_len.append(float(parts[6]))     # fosc(D2)
                except (ValueError, IndexError):
                    continue

    # Extract from velocity dipole section
    in_section = False
    i_len = 0
    for i, line in enumerate(lines):
        if "ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS" in line:
            in_section = True
            continue

        if in_section:
            stripped = line.strip()
            if stripped.startswith("-") or not stripped:
                if not stripped:
                    break
                continue

            parts = stripped.split()
            if len(parts) >= 7 and "-" in parts[0] and "A" in parts[0]:
                try:
                    if i_len < len(f_len):
                        f_vel.append(float(parts[6]))     # fosc(P2)
                        i_len += 1
                except (ValueError, IndexError):
                    continue

    return e_ev, e_nm, f_len, f_vel

def read_cd(filename: str, transition_index: int = 0) -> Tuple[float, float, float, float]:
    """
    Extract a CD transition from both electric- and velocity-dipole tables.

    Args:
        filename: Path to ORCA output file.
        transition_index: Index of transition to extract (0 = first, 1 = second, etc.).

    Returns:
        (E_eV, E_nm, R_len, R_vel) for the specified transition.

    Raises:
        ValueError: If the requested transition is not found or data is incomplete.
    """

    with open(filename) as f:
        lines = f.readlines()

    e_ev = e_nm = R_len = R_vel = None

    # Extract from electric dipole section
    in_section = False
    count = 0
    for i, line in enumerate(lines):
        if "CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
            in_section = True
            continue

        if in_section:
            stripped = line.strip()
            if stripped.startswith("-") or not stripped:
                if not stripped:
                    break
                continue

            if re.match(r"\s*\d+-\d+A", line):
                if count == transition_index:
                    parts = stripped.split()
                    try:
                        e_ev = float(parts[3])      # Energy (eV)
                        e_nm = float(parts[5])      # Wavelength (nm)
                        R_len = float(parts[6])     # R (1e40*cgs)
                    except (ValueError, IndexError):
                        pass
                    break
                count += 1

    # Extract from velocity dipole section
    in_section = False
    count = 0
    for i, line in enumerate(lines):
        if "CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS" in line:
            in_section = True
            continue

        if in_section:
            stripped = line.strip()
            if stripped.startswith("-") or not stripped:
                if not stripped:
                    break
                continue

            if re.match(r"\s*\d+-\d+A", line):
                if count == transition_index:
                    parts = stripped.split()
                    try:
                        R_vel = float(parts[6])     # R (1e40*cgs)
                    except (ValueError, IndexError):
                        pass
                    break
                count += 1

    if None in (e_ev, e_nm, R_len, R_vel):
        raise ValueError(f"CD transition {transition_index} not found in {filename}")

    return e_ev, e_nm, R_len, R_vel
