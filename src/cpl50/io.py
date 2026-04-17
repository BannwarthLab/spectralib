""" Contains parser functions. """

from __future__ import annotations

import csv
import numpy as np

from pathlib import Path
from typing import List, Dict, Optional

from cpl50.utils import Spectrum, VALID_SOLVENTS, VALID_QUANT_CP, VALID_UNIT_CP, VALID_QUANT_LUM, VALID_UNIT_LUM, DOI_REGEX


REQUIRED_FIELDS = ["DOI", "molname", "T", "c", "solv", "irrad", "quant", "unit"]


def read_spectrum(path: str) -> Spectrum:
    """ Read spectrum from .csv file and check for valid header data. 
    
    Args:
        path (str): Path to file.

    Returns:
        Spectrum dataclass containing x, y, and the header data as dict.
    """

    # Parse header line, split and build dict 
    with open(path, "r") as f:
        header = f.readline()

    parts = [p.strip() for p in header.strip().split(",")]
    if len(parts) != 8:
        raise ValueError(f"Header must have 8 fields, got {len(parts)}")

    hdict = dict(zip(REQUIRED_FIELDS, parts))
    hdict["file"] = path
    print(hdict.keys)

    # Check validity of entries
    _validate_header(hdict)

    data = np.loadtxt(path, delimiter=",", skiprows=1)

    if data.ndim != 2 or data.shape[1] != 2:
        raise ValueError("Spectrum must have exactly two columns")

    x, y = data.T

    chk = np.diff(x) > 0
    if not np.all(chk):
        print(f"File: {path}, line(s): {np.where(~chk)[0] + 2}")
        raise ValueError("x-axis must be strictly increasing")

    return Spectrum(x=x, y=y, metadata=hdict)


def _validate_header(header_data: Dict[str, str], filename: Optional[str] = None) -> None:
    # DOI must always be present and not 0
    doi = header_data["DOI"]

    if not doi:
        raise ValueError(f"Missing DOI{f' in {filename}' if filename else ''}")

    if not bool(DOI_REGEX.match(doi)):
        raise ValueError("DOI must not be '0'")
    if doi == "0":
        raise ValueError(f"DOI must not be '0'{f' in {filename}' if filename else ''}")
    if not bool(DOI_REGEX.match(doi)):
        raise ValueError(
            f"Invalid DOI format '{doi}'{f' in {filename}' if filename else ''}"
        )

    # Check temperature >= 0. If none given, 0 is valid. 
    if header_data["T"] != "0":
        T = float(header_data["T"])
        if T <= 0:
            raise ValueError("Temperature must be positive")

    # Check concentration >= 0. If none given, 0 is valid. 
    if header_data["c"] != "0":
        c = float(header_data["c"])
        if c <= 0:
            raise ValueError("Concentration must be positive")

    # Check solvent against known list. If none given, 0 is valid.
    if header_data["solv"] != "0" and header_data["solv"] not in VALID_SOLVENTS:
        raise ValueError(f"Invalid solvent: {header_data['solv']}")

    # Check irrad. wavelength >=0 . If none given, 0 is valid.
    if header_data["irrad"] != "0":
        irrad = float(header_data["irrad"])
        if irrad <= 0:
            raise ValueError("Irradiation wavelength must be positive")

    # Check that quant and unit are consistent with filename declaration. If none is given, 0 is *invalid*
    if "CPL" in header_data["file"]:
        if header_data["quant"] not in VALID_QUANT_CP:
            raise ValueError(
                f"Invalid CPL quantity '{header_data['quant']}' in {filename}. "
                #f"Expected one of {sorted(VALID_QUANT_CP)}"
            )
        
        if header_data["unit"] not in VALID_UNIT_CP:
            raise ValueError(
                f"Invalid CPL unit '{header_data['unit']}' in {filename}. "
                #f"Expected one of {sorted(VALID_UNIT_CP)}"
            )
        
    elif "LUM" in header_data["file"]:
        if header_data["quant"] not in VALID_QUANT_LUM:
            raise ValueError(
                f"Invalid LUM quantity '{header_data['quant']}' in {filename}. "
                #f"Expected one of {sorted(VALID_QUANT_LUM)}"
            )
        if header_data["unit"] not in VALID_UNIT_LUM:
            raise ValueError(
                f"Invalid LUM unit '{header_data['unit']}' in {filename}. "
                #f"Expected one of {sorted(VALID_UNIT_LUM)}"
            )
        
def read_xyz(file: str) -> tuple[np.ndarray,np.ndarray]:
    """Read xyz file.

    Args:
        file (str): Input xyz file.

    Returns:
        tuple: A tuple containing element symbols and coordinates.
    """

    elms, coords = [], []
    with open(file) as f:
        _ = f.readline()  # Skip nat
        next(f)  # Skip comment line
        for line in f.readlines():
            elms.append(line.split()[0].lower())
            coords.append([float(a) for a in line.split()[1:]])
            
    return np.array(elms, dtype=str), np.array(coords)


def sort_csv_by_x(input_file, output_file):
    """ Read a .csv file, sort by the first column (x values), and write to a new file.
    
    Args:
        input_file: Path to the input .csv file.
        output_file: Path to the output .csv file.

    Returns:
        None. 
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Keep the first line (metadata/header)
    header = lines[0].strip()

    # Parse numeric data (skip first line)
    data = []
    for line in lines[1:]:
        if line.strip():  # skip empty lines
            parts = line.strip().split(',')
            try:
                x = float(parts[0])
                y = float(parts[1])
                data.append((x, y))
            except ValueError:
                # skip malformed rows
                continue

    # Sort by x value
    data.sort(key=lambda row: row[0])

    # Write sorted data
    with open(output_file, 'w', newline='') as f:
        f.write(header + '\n')
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

def summarize_dataset(spectra_dir: str) -> str:
    """ Generate formatted printout for the dataset. """
    spectra_path = Path(spectra_dir)

    lines: List[str] = []
    lines.append("CPL50 Dataset Summary")
    lines.append("=" * 40 + "\n")

    for file in sorted(spectra_path.rglob("*.csv")):
        spec = read_spectrum(str(file))
        m = spec.metadata

        line = (
            f"{m['molname']:10s} | "
            f"T={m['T']} K | "
            f"c={m['c']} M | "
            f"solv={m['solv']} | "
            f"λ={m['irrad']} nm | "
            f"{m['quant']} ({m['unit']})"
        )

        lines.append(line)

    return "\n".join(lines)