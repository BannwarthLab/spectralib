"""spectralib: tools for the luminescence/CPL reference dataset and for comparing calculated with experimental spectra."""

from importlib.metadata import PackageNotFoundError, version

from spectralib.io import read_spectrum, read_xyz, write_spectrum
from spectralib.spectrum import Spectrum

try:
    __version__ = version("spectralib")
except PackageNotFoundError:  # running from a source tree without installation
    __version__ = "unknown"

__all__ = ["Spectrum", "__version__", "read_spectrum", "read_xyz", "write_spectrum"]
