"""Stores types and dicts to validate entries in header."""

from __future__ import annotations

import re

import numpy as np

# Required fields tested for in the header of all spectrum data
REQUIRED_FIELDS = ["DOI", "molname", "T", "c", "solv", "irrad", "quant", "unit"]

# -----  Registry of valid keys within the header in CPL50  ----- #
DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


VALID_SOLVENTS = {
    "meoh",  # methanol
    "ch3oh",
    "etoh",  # ethanol
    "h2o",  # water
    "mecn",  # acetonitrile
    "toluene",  # toluene
    "tol",
    "hexane",  # hexane
    "dcm",  # dichloromethane
    "ch2cl2",  # dcm
    "chloroform",  # chloroform
    "chcl3",
    "p-dioxane",
    "1-4-dioxane",
    "dmf",
    "chex",
    "cyclohexane",
    "ccl4",
    "me-chex",
    # "0",      # allow missing value
}


SOLVENT_ALIASES = {
    # methanol
    "meoh": "methanol",
    "ch3oh": "methanol",
    # ethanol
    "etoh": "ethanol",
    # water
    "h2o": "water",
    # acetonitrile
    "mecn": "acetonitrile",
    # toluene
    "tol": "toluene",
    "toluene": "toluene",
    # dichloromethane
    "dcm": "dichloromethane",
    "ch2cl2": "dichloromethane",
    # chloroform
    "chloroform": "chloroform",
    "chcl3": "chloroform",
    # dioxane
    "p-dioxane": "p-dioxane",
    "1-4-dioxane": "p-dioxane",
    # cyclohexane
    "chex": "cyclohexane",
    "me-chex": "methylcyclohexane",
    "cyclohexane": "cyclohexane",
    # carbon tetrachloride
    "ccl4": "carbon tetrachloride",
    # direct names
    "hexane": "hexane",
    "dmf": "dmf",
}

DIELECTRIC_CONSTANTS = {  # https://comp.chem.umn.edu/solvation/mnsddb.pdf
    "carbon tetrachloride": 2.2280,
    "dichloromethane": 8.93,
    "chloroform": 4.7113,
    "cyclohexane": 2.0165,
    "ethanol": 24.852,
    "methanol": 32.613,
    "p-dioxane": 2.2099,
    "toluene": 2.3741,
    "water": 78.3553,
    "acetonitrile": 35.6881,
    "hexane": 1.8819,
    "dmf": 37.2190,
    "methylcyclohexane": 2.024,
}


def canonicalize_solvent(solvent: str) -> str:
    """
    Convert solvent alias to canonical name.
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
