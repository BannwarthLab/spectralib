"""Stores types and dicts to validate entries in header."""

from __future__ import annotations

import re
from types import MappingProxyType

import numpy as np
from unitkit.constants.solvents import SOLVENTS_TO_DIELECTRIC_CONSTANTS, SOLVENTS_TO_REFRACTIVE_INDICES

# Required fields tested for in the header of all spectrum data
REQUIRED_FIELDS = ["DOI", "molname", "T", "c", "solv", "irrad", "quant", "unit"]

# -----  Registry of valid keys within the header in spectralib  ----- #
DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


# Accepted ``solv`` header values (lower-cased) -> canonical solvent name. The canonical names are
# the keys of the Minnesota solvent descriptor database as stored in ``unitkit.constants.solvents``,
# so all solvent properties are looked up there directly; spectralib only owns the aliases.
# Aliases must not contain commas (the header line is comma-separated): "1,4-dioxane" and
# "n,n-dimethylformamide" are therefore canonical names only, written e.g. as "1-4-dioxane" or "dmf".
SOLVENT_ALIASES = MappingProxyType(
    {
        # methanol
        "methanol": "methanol",
        "meoh": "methanol",
        "ch3oh": "methanol",
        # ethanol
        "ethanol": "ethanol",
        "etoh": "ethanol",
        # water
        "water": "water",
        "h2o": "water",
        # acetonitrile
        "acetonitrile": "acetonitrile",
        "mecn": "acetonitrile",
        "ch3cn": "acetonitrile",
        # toluene
        "toluene": "toluene",
        "tol": "toluene",
        # dichloromethane
        "dichloromethane": "dichloromethane",
        "dcm": "dichloromethane",
        "ch2cl2": "dichloromethane",
        # chloroform
        "chloroform": "chloroform",
        "chcl3": "chloroform",
        # 1,4-dioxane
        "1-4-dioxane": "1,4-dioxane",
        "p-dioxane": "1,4-dioxane",
        "dioxane": "1,4-dioxane",
        # cyclohexane
        "cyclohexane": "cyclohexane",
        "chex": "cyclohexane",
        # methylcyclohexane
        "methylcyclohexane": "methylcyclohexane",
        "me-chex": "methylcyclohexane",
        "mch": "methylcyclohexane",
        # carbon tetrachloride
        "carbon tetrachloride": "carbon tetrachloride",
        "ccl4": "carbon tetrachloride",
        # n-hexane
        "n-hexane": "n-hexane",
        "hexane": "n-hexane",
        # n,n-dimethylformamide
        "dimethylformamide": "n,n-dimethylformamide",
        "dmf": "n,n-dimethylformamide",
    }
)

#: Accepted values of the ``solv`` header field (aliases, case-insensitive).
VALID_SOLVENTS = frozenset(SOLVENT_ALIASES)

#: Canonical solvent name -> dielectric constant (relative permittivity) at 298 K,
#: from the Minnesota solvent descriptor database (https://comp.chem.umn.edu/solvation/mnsddb.pdf) via unitkit.
DIELECTRIC_CONSTANTS = MappingProxyType(
    {name: SOLVENTS_TO_DIELECTRIC_CONSTANTS[name] for name in sorted(set(SOLVENT_ALIASES.values()))}
)

#: Canonical solvent name -> refractive index n_D at 293 K, same source.
REFRACTIVE_INDICES = MappingProxyType(
    {name: SOLVENTS_TO_REFRACTIVE_INDICES[name] for name in sorted(set(SOLVENT_ALIASES.values()))}
)


def canonicalize_solvent(solvent: str) -> str:
    """Convert a solvent alias (case-insensitive) to its canonical name.

    The canonical name is the solvent's key in ``unitkit.constants.solvents``.

    Raises:
        ValueError: If the alias is not in ``SOLVENT_ALIASES``.
    """

    s = solvent.lower().strip()

    if s not in SOLVENT_ALIASES:
        raise ValueError(f"Unknown solvent alias: {solvent}")

    return SOLVENT_ALIASES[s]


VALID_QUANT_CP = {
    "cpl",
    "cpf",
    "di",
    "glum",
}

VALID_UNIT_CP = {
    "mdeg",
    "0",  # allow missing value
}

VALID_QUANT_LUM = {
    "i",  # prohibit missing value
    "dc",  # differential current (in V)?
}

VALID_UNIT_LUM = {
    "0",  # allow missing value
    "v",  # volts, only seen in https://pubs.rsc.org/en/content/articlepdf/2015/ra/c4ra11488d for 51-53 so far
}


def kabsch_rmsd(xyz1: np.ndarray, xyz2: np.ndarray) -> float:
    """Kabsch-algorithm RMSD between two centred, equally-ordered coordinate sets.

    Args:
        xyz1 (np.ndarray): Cartesian coordinates of molecule 1, shape (N, 3).
        xyz2 (np.ndarray): Cartesian coordinates of molecule 2, shape (N, 3).

    Returns:
        float: RMSD in the same units as the input coordinates (typically Å).

    Ref:
        https://en.wikipedia.org/wiki/Kabsch_algorithm
    """
    xyz1 = xyz1 - xyz1.mean(axis=0)
    xyz2 = xyz2 - xyz2.mean(axis=0)

    R = xyz1.T @ xyz2
    U, _, Vt = np.linalg.svd(R)
    V, Ut = Vt.T, U.T
    d = int(np.sign(np.linalg.det(V @ Ut)))
    correction = np.diag([1, 1, d])
    rot = V @ correction @ Ut
    xyz2_aligned = xyz2 @ rot
    return float(np.sqrt(np.mean(np.sum((xyz1 - xyz2_aligned) ** 2, axis=1))))
