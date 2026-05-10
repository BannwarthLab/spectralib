# =============================================================================
# test_structures.py  –  XYZ structure files + RMSD duplicate detection
# =============================================================================
import itertools
from pathlib import Path

import numpy as np
import re
import pytest

from cpl50.io import read_xyz
from cpl50.utils import kabsch_rmsd

RMSD_DUPLICATE_THRESHOLD = 0.1  # Å — pairs below this are flagged as duplicates

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_structures():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "structures"
    files = sorted(data_dir.rglob("*.xyz"))
    assert files, "No .xyz files found in data/structures"
    return [(f, *read_xyz(str(f))) for f in files]


# ---------------------------------------------------------------------------
# Parsing sanity
# ---------------------------------------------------------------------------

def test_read_all_structure_files(all_structures):
    for path, elements, coords in all_structures:
        assert len(elements) > 0, f"No elements in {path}"
        assert coords.shape == (len(elements), 3), f"Shape mismatch in {path}"

def test_elements_are_valid_symbols(all_structures):
    """Element symbols must be 1–2 alphabetic characters (case-insensitive)."""
    pattern = re.compile(r"^[A-Za-z]{1,2}$")
    for path, elements, _ in all_structures:
        bad = [e for e in elements if not pattern.match(e)]
        assert not bad, f"Unexpected element symbols in {path.name}: {bad}"

def test_no_nan_or_inf_coordinates(all_structures):
    for path, _, coords in all_structures:
        assert np.isfinite(coords).all(), f"Non-finite coordinates in {path.name}"

def test_atom_count_matches_header(all_structures):
    """read_xyz already checks this, but we confirm the fixture is consistent."""
    for path, elements, coords in all_structures:
        assert len(elements) == coords.shape[0], f"Atom count mismatch in {path.name}"


# ---------------------------------------------------------------------------
# Naming convention
# ---------------------------------------------------------------------------

_STEM_RE = re.compile(r"^(\d+)([a-z]*)$")

def test_structure_filenames_match_convention(all_structures):
    """Stems must be <int> or <int><lowercase-letters>, e.g. 1, 33a, 33b, 33ab."""
    for path, _, __ in all_structures:
        stem = path.stem
        assert _STEM_RE.match(stem), (
            f"Structure filename '{path.name}' does not match convention "
            f"'<int>[a-z]*' (e.g. 33a, 33ab)"
        )

# ---------------------------------------------------------------------------
# RMSD duplicate detection
# ---------------------------------------------------------------------------

def test_no_duplicate_structures(all_structures):
    """No two structures with the same atom count and element composition
    should be near-identical (Kabsch RMSD < threshold).

    Note: enantiomers will superimpose under Kabsch (which corrects for
    reflections via the determinant sign). If your dataset intentionally
    contains enantiomeric pairs, exclude them here by stem label.
    """
    from collections import defaultdict

    by_size: dict[int, list] = defaultdict(list)
    for path, elements, coords in all_structures:
        by_size[len(elements)].append((path, elements, coords))

    duplicates: list[str] = []
    for group in by_size.values():
        for (p1, el1, c1), (p2, el2, c2) in itertools.combinations(group, 2):
            if sorted(el1) != sorted(el2):
                continue
            rmsd = kabsch_rmsd(c1.copy(), c2.copy())
            if rmsd < RMSD_DUPLICATE_THRESHOLD:
                duplicates.append(
                    f"  RMSD={rmsd:.4f} Å  {p1.name}  vs  {p2.name}"
                )

    assert not duplicates, (
        f"{len(duplicates)} duplicate pair(s) found "
        f"(threshold {RMSD_DUPLICATE_THRESHOLD} Å):\n" + "\n".join(duplicates)
    )