""" Contains parser functions. """

from __future__ import annotations

import csv
import re
import numpy as np

from pathlib import Path
from typing import Tuple, List, Dict, Optional, Union

from cpl50.utils import (
    REQUIRED_FIELDS,
    DOI_REGEX,
    VALID_QUANT_CP,
    VALID_QUANT_LUM,
    VALID_SOLVENTS,
    VALID_UNIT_CP,
    VALID_UNIT_LUM,
    Spectrum
)

def read_spectrum(path: str) -> Spectrum:
    """ Read spectrum from .csv file and check for valid header data. 
    
    Args:
        path (str): Path to the .csv file.

    Returns:
        Spectrum: Dataclass containing x, y arrays and the header as metadata dict.

    Raises:
        ValueError: If the header does not have exactly 8 fields.
        ValueError: If any header field fails validation (see _validate_header).
        ValueError: If the data block does not have exactly two columns.
        ValueError: If the x-axis is not strictly increasing.
    """

    # Parse header line, split and build dict 
    with open(path, "r") as f:
        header = f.readline()

    parts = [p.strip() for p in header.strip().split(",")]
    if len(parts) != 8:
        raise ValueError(f"Header must have 8 fields, got {len(parts)} in {path}")

    hdict = dict(zip(REQUIRED_FIELDS, parts))
    hdict["file"] = path
    
    # Check validity of entries
    _validate_header(hdict)

    data = np.loadtxt(path, delimiter=",", skiprows=1)

    if data.ndim != 2 or data.shape[1] != 2:
        raise ValueError(f"Spectrum must have exactly two columns in {path}")

    x, y = data.T
    chk = np.diff(x) > 0
    if not np.all(chk):
        failed_lines = np.where(~chk)[0] + 2
        raise ValueError(
            f"x-axis must be strictly increasing in {path};" 
            f"wrong line(s): {failed_lines.tolist()}"
            )

    return Spectrum(x=x, y=y, metadata=hdict)



def _validate_header(header_data: Dict[str, str], filename: Optional[str] = None) -> None:
    """ Check that entries in header are valid for both LUM and CPL files. 

    Args:
        header_data (Dict[str, str]): Parsed header fields. 
    
    Returns:
        None. 

    Notes:
        Expected keys in header_data:
        - DOI: must match DOI_REGEX, cannot be 0.
        - T: Temperature, or 0 if not reported.
        - c: Concentration, or 0 if not reported.
        - solv: Solvent name, cannot be 0.
        - irrad: Irradiation wavelength, or 0 if not reported.
        - file: Original filename used to infer file spectra type (CPL or LUM).
        - quant: Measured quantity; cannot be 0.
        - unit: Unit of quant, or 0 if dimensioless/not reported.

    Raises:
        ValueError: If DOI is missing, 0, or does not match DOI_REGEX.
        ValueError: If T is provided, but <0.
        ValueError: If c is provided but <0.
        ValueError: If solv is provided but not in VALID_SOLVENTS.
        ValueError: If irrad is provided but <100.
        ValueError: If quant or unit are inconsistent with file type (CPL or LUM).
    """

    filename = header_data["file"]
    fstem = Path(filename).stem.upper()

    # DOI must always be present and not 0
    doi = header_data["DOI"]
    if not doi:
        raise ValueError(f"Missing DOI in {filename}")
    if doi == "0":
        raise ValueError(f"DOI must not be '0' in {filename}")
    if not DOI_REGEX.match(doi):
        raise ValueError(f"Invalid DOI format '{doi}' in {filename}")

    # Temperature (optional), but must be positive if given
    if header_data["T"] != "0":
        T = float(header_data["T"])
        if T <= 0:
            raise ValueError(f"Temperature must be positive in {filename}")

    # Concentration (optional), but must be positive if given
    if header_data["c"] != "0":
        c = float(header_data["c"])
        if c <= 0:
            raise ValueError(f"Concentration must be positive in {filename}")

    # Solvent has to be in known solvent 
    if header_data["solv"].lower() not in VALID_SOLVENTS:
        raise ValueError(f"Invalid solvent '{header_data['solv']}' in {filename}")

    # Irradiation wavelength (optional), but if != 0, should be >= 100
    if header_data["irrad"] != "0":
        irrad = float(header_data["irrad"])
        if irrad < 100:
            raise ValueError(f"Irradiation wavelength must be >= 100 in {filename}")

    # Measured Quantity and unit, must match declared file type
    if "CPL" in fstem:
        if header_data["quant"].lower() not in VALID_QUANT_CP:
            raise ValueError(f"Invalid CPL quantity '{header_data['quant']}' in {filename}")
        if header_data["unit"].lower() not in VALID_UNIT_CP:
            raise ValueError(f"Invalid CPL unit '{header_data['unit']}' in {filename}")
        
    elif "LUM" in fstem:
        if header_data["quant"].lower() not in VALID_QUANT_LUM:
            raise ValueError(f"Invalid LUM quantity '{header_data['quant']}' in {filename}")
        if header_data["unit"].lower() not in VALID_UNIT_LUM:
            raise ValueError(f"Invalid LUM unit '{header_data['unit']}' in {filename}")
        
def read_xyz(file: str) -> Tuple[np.ndarray,np.ndarray]:
    """Read xyz file.

    Args:
        file (str): Input xyz file.

    Returns:
        tuple: A tuple containing element symbols and coordinates.
    
    Raises:
        ValueError: If parsed number of atoms in first line does not match length of element symbol list
    """

    elms : List[str] = []
    coords : List[List[float]] = []

    with open(file) as f:
        nat = int(f.readline().strip())
        f.readline()  # Skip comment line
        for line in f:
            lin = line.strip()
            if not lin:
                continue
            elms.append(lin.split()[0].lower()) # store lower case elements
            coords.append([float(a) for a in lin.split()[1:4]])

    #
    if len(elms) != nat:
        raise ValueError(
            f"Expected {nat} atoms in {file}, found {len(elms)}"
        )
            
    return np.array(elms, dtype=str), np.array(coords)


def sort_csv_by_x(input_file : str, output_file : str) -> None:
    """ Read a .csv file, sort rows by the first column, and write to a new file.
    
    Args:
        input_file (str): Path to the input .csv file.
        output_file (str): Path to the output .csv file.

    Returns:
        None. 
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Keep header
    header = lines[0].strip()

    rows : List[Tuple[float, float]] = []
    for line in lines[1:]:
        lin = line.strip()
        if not lin: # skip empty lines
            continue
        parts = line.strip().split(',')

        rows.append((float(parts[0]), float(parts[1])))


    # Sort by x value
    rows.sort(key=lambda row: row[0])

    # Write sorted data
    with open(output_file, 'w', newline='') as f:
        f.write(header + '\n')
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def write_spectrum(
    spectrum: Spectrum,
    path: Union[str, Path],
    overwrite: bool = False,
) -> None:
    """Write Spectrum to .csv file including metadata as header.
    The header order is defined by REQUIRED_FIELDS.


    Args:
        spectrum (Spectrum): Spectrum to write to csv.

        path (str | Path):
            Output file path.

        overwrite (bool):
            If False, raises if file already exists.

    Raises:
        - FileExistsError: If file exists and overwrite=False.
        - ValueError: If required metadata fields are missing.
        - ValueError: If metadata validation fails.
    """

    path = Path(path)

    if path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {path}"
        )

    # ------------------------------------------------------------------
    # Validate metadata
    # ------------------------------------------------------------------

    missing = [
        field for field in REQUIRED_FIELDS
        if field not in spectrum.metadata
    ]

    if missing:
        raise ValueError(
            f"Spectrum metadata missing required fields: {missing}"
        )

    # preserve exact header ordering
    # hdict = {
    #     field: str(spectrum.metadata[field])
    #     for field in REQUIRED_FIELDS
    # }

    _validate_header(spectrum.metadata)

    # ------------------------------------------------------------------
    # Build header line
    # ------------------------------------------------------------------

    header = ",".join(
        str(spectrum.metadata[field]).strip()
        for field in REQUIRED_FIELDS
    )

    # ------------------------------------------------------------------
    # Build data block
    # ------------------------------------------------------------------

    data = np.column_stack((spectrum.x, spectrum.y))

    # ------------------------------------------------------------------
    # Write file
    # ------------------------------------------------------------------

    with open(path, "w", newline="\n") as f:

        # write header manually
        f.write(header + "\n")

        # append numeric block
        np.savetxt(
            f,
            data,
            delimiter=",",
        )

def summarize_dataset(spectra_dir: str, select: Optional[List[int]] = None) -> None:
    """Generate formatted printout of all spectra in dataset directory.

    Each spectrum is listed with its header data, sorted by numeric molecule ID.
    Files that fail to parse are reported as errors rather than aborting the summary.
    Optional fields with sentinel value '0' are shown as '-'.

    Args:
        spectra_dir (str): Path to root dir containing .csv files.
        select (Optional[List[int]]): If given, only print entries whose leading
            numeric ID is in this list. E.g. select=[1, 33, 60].
    """
    spectra_path = Path(spectra_dir)
    files = sorted(spectra_path.rglob("*.csv"))

    _ID_RE = re.compile(r"^(\d+)")

    def _sort_key(p: Path) -> Tuple:
        m = _ID_RE.match(p.stem)
        return (int(m.group(1)), p.stem) if m else (float("inf"), p.stem)

    def _id(p: Path) -> Optional[int]:
        m = _ID_RE.match(p.stem)
        return int(m.group(1)) if m else None

    files = sorted(files, key=_sort_key)

    if select is not None:
        select_set = set(select)
        files = [f for f in files if _id(f) in select_set]

    def _fmt(value: str, suffix: str = "") -> str:
        return f"{value.lower()}{suffix}" if value != "0" else "-"

    def _trunc(s: str, width: int) -> str:
        """Truncate string to width, appending … if cut."""
        return s if len(s) <= width else s[: width - 1] + "…"

    COL = {
        "file":   20,
        "mol":    16,
        "doi":    36,
        "T":      10,
        "c":      10,
        "solv":   12,
        "irrad":  10,
        "quant":   6,
        "unit":    6,
    }

    def _row(
        file: str, mol: str, doi: str,
        T: str, c: str, solv: str,
        irrad: str, quant: str, unit: str,
        error: str = "",
    ) -> str:
        if error:
            return f"  {'ERROR':{COL['file']}}  {file:<50}  {error}"
        return (
            f"  {_trunc(file,  COL['file'])  :{COL['file']}}"
            f"  {_trunc(mol,   COL['mol'])   :{COL['mol']}}"
            f"  {_trunc(doi,   COL['doi'])   :{COL['doi']}}"
            f"  {T              :{COL['T']}}"
            f"  {c              :{COL['c']}}"
            f"  {_trunc(solv,  COL['solv'])  :{COL['solv']}}"
            f"  {irrad          :{COL['irrad']}}"
            f"  {quant          :{COL['quant']}}"
            f"  {unit           :{COL['unit']}}"
        )

    header_row = _row(
        file="File", mol="Molecule", doi="DOI",
        T="T (K)", c="c (M)", solv="Solvent",
        irrad="λirr (nm)", quant="Quant", unit="Unit",
    )
    sep_width = sum(COL.values()) + 2 * len(COL) + 2
    separator  = "-" * sep_width
    thin_sep   = "·" * sep_width

    lines: List[str] = [
        "",
        "  CPL50 Dataset Summary",
        f"  {len(files)} file(s) in {spectra_dir}",
        "",
        header_row,
        separator,
    ]

    n_ok  = 0
    n_err = 0
    prev_id: Optional[int] = None

    for file in files:
        current_id = _id(file)
        short_name = file.name

        # Blank line between groups (different leading ID)
        if prev_id is not None and current_id != prev_id:
            lines.append(thin_sep)

        try:
            spec = read_spectrum(str(file))
            m = spec.metadata
            lines.append(_row(
                file=short_name,
                mol=m["molname"],
                doi=m["DOI"],
                T=_fmt(m["T"], " K"),
                c=_fmt(m["c"], " M"),
                solv=_fmt(m["solv"]),
                irrad=_fmt(m["irrad"], " nm"),
                quant=m["quant"].lower(),
                unit=_fmt(m["unit"]),
            ))
            n_ok += 1
        except Exception as exc:
            lines.append(_row(
                file="", mol="", doi="", T="", c="",
                solv="", irrad="", quant="", unit="",
                error=f"{short_name}: {exc}",
            ))
            n_err += 1

        prev_id = current_id

    lines += [
        separator,
        f"  {n_ok} parsed successfully,  {n_err} error(s).",
        "",
    ]

    print("\n".join(lines))