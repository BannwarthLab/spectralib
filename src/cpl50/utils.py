""" Stores types and dicts to validate entries in header. """

from __future__ import annotations

import re
import numpy as np
from dataclasses import dataclass
from typing import Dict

@dataclass
class Spectrum:
    x: np.ndarray
    y: np.ndarray
    metadata: Dict[str, str]


# Matches the integer suffix for repeated-condition files, e.g. "1_CPL_1.csv" -> suffix "_1"
_CONDITION_SUFFIX_RE = re.compile(r"_\d+$")

# Required fields tested for in the header of all spectrum data
REQUIRED_FIELDS = ["DOI", "molname", "T", "c", "solv", "irrad", "quant", "unit"]

# -----  Registry of valid keys within the header in CPL50  ----- #
DOI_REGEX = re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.IGNORECASE)

VALID_SOLVENTS = {
    "meoh",   # methanol
    "ch3oh",  
    "etoh",   # ethanol
    "h2o",    # water
    "mecn",    # acetonitrile
    "toluene", # toluene
    "tol",
    "hexane", # hexane
    "dcm", # dichloromethane
    "ch2cl2", # dcm
    "chloroform", # chloroform
    "chcl3", 
    "p-dioxane",
    "1-4-dioxane",
    "dmf",
    "chex",
    "cyclohexane",
    "ccl4",
    "me-chex",
    #"0",      # allow missing value
}

VALID_QUANT_CP = {
    "cpl",
    "cpf",
    "di",
    "glum",
}

VALID_UNIT_CP = {
    "mdeg",
    "0" # allow missing value
}

VALID_QUANT_LUM = {
    "i", # prohibit missing value
    "dc", # differential current (in V)? 
}

VALID_UNIT_LUM = {
    "0", # allow missing value
    "v" # volts, only seen in https://pubs.rsc.org/en/content/articlepdf/2015/ra/c4ra11488d for 51-53 so far
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