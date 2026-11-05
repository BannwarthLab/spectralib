"""Dataset-level helpers: header metadata of all spectra, a printed summary and simple queries."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from spectralib.io import read_spectrum

# ---------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------

_ID_RE = re.compile(r"^(\d+)")


def _id(path: Path) -> int | None:
    """Extract leading numeric ID from filename."""
    m = _ID_RE.match(path.stem)
    return int(m.group(1)) if m else None


def _sort_key(path: Path) -> tuple:
    """Sort by leading numeric ID, then filename."""
    mol_id = _id(path)
    return (mol_id if mol_id is not None else float("inf"), path.stem)


def _clean(value: str) -> str:
    """Normalize sentinel values."""
    if value == "0":
        return "-"
    return value.lower()


def load_dataset_metadata(
    spectra_dir: str | Path,
    select: list[int] | None = None,
) -> list[dict[str, Any]]:
    """
    Load metadata records from all spectra.

    Args:
        spectra_dir:
            Root directory containing CSV spectra.

        select:
            Optional list of molecule IDs to include.

    Returns:
        List of metadata dictionaries.
    """

    spectra_path = Path(spectra_dir)

    files = sorted(
        spectra_path.rglob("*.csv"),
        key=_sort_key,
    )

    if select is not None:
        select_set = set(select)
        files = [f for f in files if _id(f) in select_set]

    records = []

    for file in files:
        try:
            spec = read_spectrum(str(file))
            m = spec.metadata

            records.append(
                {
                    "id": _id(file),
                    "file": file.name,
                    "path": str(file),
                    "mol": _clean(m["molname"]),
                    "doi": _clean(m["DOI"]),
                    "T": _clean(m["T"]),
                    "c": _clean(m["c"]),
                    "solv": _clean(m["solv"]),
                    "irrad": _clean(m["irrad"]),
                    "quant": _clean(m["quant"]),
                    "unit": _clean(m["unit"]),
                }
            )

        except (ValueError, OSError) as exc:
            records.append(
                {
                    "id": _id(file),
                    "file": file.name,
                    "error": str(exc),
                }
            )

    return records


# ---------------------------------------------------------------------
# Pretty summary printer
# ---------------------------------------------------------------------


def summarize_dataset(
    records: str | Path | list[dict[str, Any]],
    columns: list[str] | None = None,
) -> None:
    """
    Pretty-print dataset summary.

    Args:
        records:
            Either a path to a spectra directory or the output from
            load_dataset_metadata().

        columns:
            Columns to display.
    """

    if isinstance(records, (str, Path)):
        records = load_dataset_metadata(str(records))

    COLS: dict[str, dict[str, Any]] = {
        "file": {"title": "File", "width": 20},
        "mol": {"title": "Molecule", "width": 16},
        "doi": {"title": "DOI", "width": 36},
        "T": {"title": "T (K)", "width": 10},
        "c": {"title": "c (M)", "width": 10},
        "solv": {"title": "Solvent", "width": 14},
        "irrad": {"title": "λirr (nm)", "width": 10},
        "quant": {"title": "Quant", "width": 8},
        "unit": {"title": "Unit", "width": 8},
    }

    DEFAULT_COLUMNS = [
        "file",
        "mol",
        "doi",
        "T",
        "c",
        "solv",
        "irrad",
        "quant",
        "unit",
    ]

    if columns is None:
        columns = DEFAULT_COLUMNS

    invalid = [c for c in columns if c not in COLS]
    if invalid:
        raise ValueError(f"Unknown columns: {invalid}")

    def trunc(s: str, width: int) -> str:
        s = str(s)
        return s if len(s) <= width else s[: width - 1] + "…"

    def row(values: dict[str, Any]) -> str:

        parts = []

        for col in columns:
            width = COLS[col]["width"]
            val = str(values.get(col, "-"))

            if col in {"file", "mol", "doi", "solv"}:
                val = trunc(val, width)

            parts.append(f"{val:{width}}")

        return "  " + "  ".join(parts)

    header = row({c: COLS[c]["title"] for c in columns})

    sep_width = sum(COLS[c]["width"] for c in columns) + 2 * len(columns)
    separator = "-" * sep_width

    print()
    print("  spectralib Dataset Summary")
    print(f"  {len(records)} records")
    print()
    print(header)
    print(separator)

    n_ok = 0
    n_err = 0

    for rec in records:
        if "error" in rec:
            print(f"  ERROR  {rec['file']}: {rec['error']}")
            n_err += 1
            continue

        print(row(rec))
        n_ok += 1

    print(separator)
    print(f"  {n_ok} parsed successfully, {n_err} error(s).")
    print()


# ---------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------


def get_solvents(
    records: list[dict[str, Any]],
    unique: bool = False,
) -> list[str]:
    """
    Return the solvents of all records (unique=True: sorted, without repeats).
    """

    solvents = [r["solv"] for r in records if "solv" in r and r["solv"] not in {"-", ""}]
    return sorted(set(solvents)) if unique else solvents


def count_solvents(
    records: list[dict[str, Any]],
) -> Counter:
    """
    Count solvent occurrences.
    """

    return Counter(r["solv"] for r in records if "solv" in r and r["solv"] not in {"-", ""})


def filter_records(
    records: list[dict[str, Any]],
    **criteria,
) -> list[dict[str, Any]]:
    """
    Filter records by metadata fields.

    Example:
        filter_records(records, solv="methanol")
    """

    out = []

    for r in records:
        match = True

        for key, value in criteria.items():
            if r.get(key) != value:
                match = False
                break

        if match:
            out.append(r)

    return out


def get_solvents_by_molecule(records: list[dict[str, Any]]) -> dict[int, str]:
    """
    Return one solvent per molecule ID.
    """

    solvents = {}

    for r in records:
        if "solv" not in r:
            continue

        mol_id = r["id"]
        solv = r["solv"]

        if solv in {"-", ""}:
            continue

        solvents[mol_id] = solv

    return solvents
