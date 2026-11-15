# =============================================================================
# test_solvents.py
# =============================================================================
"""Solvent aliases in spectralib map onto the solvent table of unitkit."""

import pytest
from unitkit.constants.solvents import SOLVENTS_TO_DIELECTRIC_CONSTANTS

from spectralib.utils import (
    DIELECTRIC_CONSTANTS,
    REFRACTIVE_INDICES,
    SOLVENT_ALIASES,
    VALID_SOLVENTS,
    canonicalize_solvent,
)

CANONICAL = set(SOLVENT_ALIASES.values())


def test_canonical_names_exist_in_unitkit():
    """Every canonical name is a key of the Minnesota table in unitkit (no second name mapping)."""
    assert CANONICAL <= set(SOLVENTS_TO_DIELECTRIC_CONSTANTS)


@pytest.mark.parametrize("alias", sorted(SOLVENT_ALIASES))
def test_alias_is_header_safe(alias):
    """Aliases are matched lower-cased and must survive the comma-separated header split."""
    assert alias == alias.lower().strip()
    assert "," not in alias


def test_comma_free_canonical_names_are_accepted():
    """A canonical name is itself a valid ``solv`` value, unless it contains a comma."""
    assert {n for n in CANONICAL if "," not in n} <= VALID_SOLVENTS


def test_properties_cover_all_canonical_names():
    assert set(DIELECTRIC_CONSTANTS) == CANONICAL
    assert set(REFRACTIVE_INDICES) == CANONICAL
    assert all(eps >= 1.0 for eps in DIELECTRIC_CONSTANTS.values())
    assert all(1.0 < n < 2.0 for n in REFRACTIVE_INDICES.values())


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("CH2Cl2", "dichloromethane"),
        (" Tol ", "toluene"),
        ("1-4-dioxane", "1,4-dioxane"),
        ("DMF", "n,n-dimethylformamide"),
    ],
)
def test_canonicalize_solvent(alias, canonical):
    assert canonicalize_solvent(alias) == canonical


def test_canonicalize_unknown_raises():
    with pytest.raises(ValueError, match="Unknown solvent"):
        canonicalize_solvent("unobtainium")


@pytest.mark.dataset
def test_dataset_solvents_have_properties(data_dir):
    """Every solvent used in the dataset resolves to a dielectric constant and refractive index."""
    for csv in sorted(data_dir.glob("spectra/*/*.csv")):
        solv = csv.read_text(encoding="utf-8").splitlines()[0].split(",")[4]
        name = canonicalize_solvent(solv)
        assert name in DIELECTRIC_CONSTANTS, csv
        assert name in REFRACTIVE_INDICES, csv
