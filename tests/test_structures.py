# =============================================================================
# test_structures.py  –  XYZ structure files, duplicates and enantiomers
# =============================================================================
import itertools
import re

import numpy as np
import pytest
from conftest import DATA

from spectralib.io import read_xyz
from spectralib.utils import kabsch_rmsd

RMSD_DUPLICATE_THRESHOLD = 0.1  # Å — pairs below this are flagged as duplicates

# every test here validates the dataset itself
pytestmark = pytest.mark.dataset

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_structures():
    data_dir = DATA / "structures"
    files = sorted(data_dir.rglob("*.xyz"))
    assert files, f"No .xyz files found in {data_dir}"
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
    should be near-identical (Kabsch RMSD < threshold)."""
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


# ---------------------------------------------------------------------------
# Duplicates and enantiomers from the MolBar identifiers
# ---------------------------------------------------------------------------
ALLOWED_STEREOISOMER_PAIRS: set[frozenset[str]] = set()


def _molbar_parts(barcode: str) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """(sections without name and version, chirality spectrum) of a MolBar."""
    sections = [s.strip() for s in barcode.strip().split("|")]
    return tuple(sections[2:-1]), tuple(int(v) for v in sections[-1].split())


def _mirror(chirality: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(-v for v in chirality))


def _stereo_relation(barcode1: str, barcode2: str) -> str | None:
    """'identical', 'enantiomers' or None (different molecules or diastereomers)."""
    (rest1, chir1), (rest2, chir2) = _molbar_parts(barcode1), _molbar_parts(barcode2)
    if rest1 != rest2:
        return None
    if chir1 == chir2:
        return "identical"
    if chir2 == _mirror(chir1):
        return "enantiomers"
    return None


def test_stereo_relation_rules():
    base = "MolBar | 1.2.0 | C2H2 | 0 | 1 | 1 2 | 3 | 4 5 | "
    assert _stereo_relation(base + "-4 0 14", base + "-4 0 14") == "identical"
    assert _stereo_relation(base + "-4 0 14", base + "-14 0 4") == "enantiomers"
    assert _stereo_relation(base + "-4 0 14", base + "-4 0 15") is None
    assert _stereo_relation(base + "0 0", base + "0 0") == "identical"
    assert _stereo_relation(base + "-10", base.replace("4 5", "4 6") + "10") is None


def test_no_duplicate_or_enantiomer_molbar():
    """No two structures may have the same MolBar or mirror-image MolBars."""
    files = sorted((DATA / "structures").rglob("*.molbar"))
    assert files, "No .molbar files found"
    barcodes = {f.stem: f.read_text() for f in files}
    found = []
    for a, b in itertools.combinations(barcodes, 2):
        relation = _stereo_relation(barcodes[a], barcodes[b])
        if relation and frozenset((a, b)) not in ALLOWED_STEREOISOMER_PAIRS:
            found.append(f"  {a} and {b}: {relation}")
    assert not found, (
        "Structures that are duplicates or enantiomers of each other (MolBar):\n"
        + "\n".join(found)
        + "\nEach system should be stored once, with the enantiomer measured in the article."
    )
