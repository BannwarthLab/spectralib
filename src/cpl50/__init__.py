"""cpl50: dataset tools and spectra comparison for the CPL50 benchmark."""

from cpl50.io import read_spectrum, read_xyz
from cpl50.spectrum import Spectrum

__all__ = ["Spectrum", "read_spectrum", "read_xyz"]
