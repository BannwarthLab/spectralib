# =============================================================================
# test_consistency.py  –  spectra and structures belong together
# =============================================================================
"""Cross-checks between data/spectra and data/structures (file layout of the dataset)."""

import re

import pytest
from conftest import DATA

pytestmark = pytest.mark.dataset

SPECTRA = DATA / "spectra"
STRUCTURES = DATA / "structures"

# <id><labels>_<LUM|CPL>[_<int>].csv, e.g. 9_CPL.csv, 41ab_CPL.csv, 25_LUM_1.csv
SPECTRUM_NAME = re.compile(r"^(?P<id>\d+)(?P<labels>[a-z]*)_(LUM|CPL)(_\d+)?\.csv$")


def _system_dirs(root):
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def test_same_systems_in_spectra_and_structures():
    """Every system has spectra and a structure folder, and vice versa."""
    assert _system_dirs(SPECTRA) == _system_dirs(STRUCTURES)


@pytest.mark.parametrize("csv", sorted(SPECTRA.glob("*/*.csv")), ids=lambda p: p.name)
def test_spectrum_name_and_structures(csv):
    """File name follows the convention, sits in its system folder, and every labelled molecule has an xyz file."""
    m = SPECTRUM_NAME.match(csv.name)
    assert m, f"{csv.relative_to(DATA)} does not match <id>[labels]_<LUM|CPL>[_<int>].csv"
    sys_id = m["id"]
    assert csv.parent.name == sys_id, f"{csv.relative_to(DATA)} is not in folder spectra/{sys_id}"
    stems = [sys_id + label for label in m["labels"]] or [sys_id]
    for stem in stems:
        xyz = STRUCTURES / sys_id / f"{stem}.xyz"
        assert xyz.is_file(), f"{csv.relative_to(DATA)} needs {xyz.relative_to(DATA)}"


@pytest.mark.parametrize("xyz", sorted(STRUCTURES.glob("*/*.xyz")), ids=lambda p: p.name)
def test_every_structure_is_used(xyz):
    """No orphaned structures: each xyz belongs to at least one spectrum of its system."""
    used = set()
    for csv in (SPECTRA / xyz.parent.name).glob("*.csv"):
        m = SPECTRUM_NAME.match(csv.name)
        if m:
            used.update([m["id"] + label for label in m["labels"]] or [m["id"]])
    assert xyz.stem in used, f"{xyz.relative_to(DATA)} is not referenced by any spectrum"


def _bib_dois(bib_file):
    """DOIs of all entries in a BibTeX file (lower case)."""
    text = bib_file.read_text(encoding="utf-8")
    return {m.lower() for m in re.findall(r"^\s*doi\s*=\s*[{\"]([^}\"]+)[}\"]", text, re.IGNORECASE | re.MULTILINE)}


def test_every_doi_has_a_reference():
    """Each header DOI has an entry in docs/source/spectralib.bib (the overview table in data.rst is built from it)."""
    bib = _bib_dois(DATA.parent / "docs" / "source" / "spectralib.bib")
    missing = sorted(
        {
            f"{csv.relative_to(DATA)}: {doi}"
            for csv in SPECTRA.glob("*/*.csv")
            if (doi := csv.read_text(encoding="utf-8").splitlines()[0].split(",")[0].strip()).lower() not in bib
        }
    )
    assert not missing, "DOIs without entry in spectralib.bib:\n" + "\n".join(missing)
