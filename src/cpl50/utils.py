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

# -----  Registry of valid keys within the header in CPL50  ----- #
DOI_REGEX = re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.IGNORECASE)

VALID_SOLVENTS = {
    "meoh",   # methanol
    "ch3oh",  
    "etoh",   # ethanol
    "h2o",    # water
    "acn",    # acetonitrile
    "dcm",    # dichloromethane
    "toluene", # toluene
    "tol",
    "hexane", # hexane
    "dcm",
    "ch2cl2", # dcm
    "chloroform", # chloroform
    "chcl3", 
    "p-dioxane",
    "0",      # allow missing value
}

VALID_QUANT_CP = {
    "cpl",
    "cpf",
    "di",
    "0",  # prohibit missing value
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