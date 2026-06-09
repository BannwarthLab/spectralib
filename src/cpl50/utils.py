""" Stores types and dicts to validate entries in header. """

from __future__ import annotations

import re
import numpy as np
import scipy.constants as sc
from typing import Dict, Optional


EN_UNITS = {"nm", "ev", "cm-1"}

# Energy conversion constant: hc in eV*nm (for E(eV) * λ(nm) conversions)
NM_TO_EV_CM = sc.h * sc.c * 1e9 / sc.e

_NM_TO = {
    "nm"  : lambda x: x,
    "ev"  : lambda x: (sc.h * sc.c * 1e9) / (x * sc.e),
    "cm-1": lambda x: 1e7 / x,
}
_TO_NM = {
    "nm"  : lambda x: x,
    "ev"  : lambda x: (sc.h * sc.c * 1e9) / (x * sc.e),
    "cm-1": lambda x: 1e7 / x,
}


class Spectrum:
    """A spectrum consisting of x/y arrays, an x-axis unit, and optional metadata.

    Can be constructed directly from arrays for standalone use, or via
    read_spectrum() which populates metadata from a .csv header.
    The x-axis unit is tracked explicitly so that convert_x() can be
    called without repeating the current unit at every call site.

    Args:
        x (np.ndarray): x-axis values, must be strictly increasing.
        y (np.ndarray): y-axis values.
        xunit (str): Unit of the x-axis. One of 'nm', 'ev', 'cm-1'.
            Defaults to 'nm', consistent with raw .csv files.
        metadata (Dict[str, str], optional): Parsed header fields. Defaults to {}.

    Raises:
        ValueError: If x and y shapes differ.
        ValueError: If x is not strictly increasing.
        ValueError: If xunit is not in EN_UNITS.
    """

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        xunit: str = "nm",
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        
        # check dimensions
        if x.shape != y.shape:
            raise ValueError(
                f"x and y must have the same shape, got {x.shape} vs {y.shape}"
            )
        
        # check monotonically increasing x
        if not np.all(np.diff(x) > 0):
            raise ValueError("x must be strictly increasing.")
        
        # check energy unit
        xunit = xunit.lower()
        if xunit not in EN_UNITS:
            raise ValueError(f"Unknown xunit '{xunit}'. Choose from {EN_UNITS}.")

        self.x        = x
        self.y        = y
        self.xunit    = xunit
        self.metadata = metadata or {}

    def scale_y(self, scal : float) -> Spectrum:
        """ Return spectrum scaled in y. 
        
        Args:
            scal (float): Scaling factor to apply
        
        Returns:
            scaled Spectrum class.
        """
        return Spectrum(x=self.x, y=self.y * scal,
                        xunit=self.xunit, metadata=self.metadata)

    def convert_x(self, final: str) -> Spectrum:
        """Convert spectrum from self.xunit to different energy unit.
        Conversion is done via nm scale, as this is the default in the experimental .csv files atm. Reorders x,y, if converted to reciprocal energy unit, e.g. nm -> eV

        Args:
            final (str): Target unit. One of 'nm', 'ev', 'cm-1'.

        Returns:
            Spectrum: New instance with converted x-axis and updated xunit.

        Raises:
            ValueError: If final is not in EN_UNITS.
        """
        final = final.lower()
        if final not in EN_UNITS:
            raise ValueError(f"Unknown unit '{final}'. Choose from {EN_UNITS}.")
        if final == self.xunit:
            return Spectrum(x=self.x.copy(), y=self.y.copy(),
                            xunit=self.xunit, metadata=self.metadata)

        x_new = _NM_TO[final](_TO_NM[self.xunit](self.x))
        order = np.argsort(x_new)
        return Spectrum(x=x_new[order], y=self.y[order],
                        xunit=final, metadata=self.metadata)

    def __len__(self) -> int:
        return len(self.x)

    def __repr__(self) -> str:
        mol = self.metadata.get("molname", "")
        id_ = f"mol={mol}, " if mol else ""
        return (
            f"Spectrum({id_}n={len(self)}, "
            f"x=[{self.x[0]:.4f}, {self.x[-1]:.4f}] {self.xunit})"
        )


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
    #"chloroform": "chloroform",
    "chcl3": "chloroform",
    # dioxane
    "p-dioxane": "p-dioxane",
    "1-4-dioxane": "p-dioxane",
    # cyclohexane
    "chex": "cyclohexane",
    "cyclohexane": "cyclohexane",
    # carbon tetrachloride
    "ccl4": "carbon tetrachloride",
    # direct names
    "hexane": "hexane",
    "dmf": "dmf",
}

DIELECTRIC_CONSTANTS = { # https://comp.chem.umn.edu/solvation/mnsddb.pdf
    "carbon tetrachloride" : 2.2280,
    "dichloromethane" : 8.93, 
    "chloroform" : 4.7113,
    "cyclohexane" : 2.0165,
    "ethanol" : 24.852,
    "methanol" : 32.613,
    "p-dioxane" : 2.2099,
    "toluene" : 2.3741, 
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