from pathlib import Path
from cpl50.io import read_spectrum

def test_all_spectra_parse():
    base = Path("data/spectra")

    for file in base.rglob("*.csv"):
        print("file:", file)
        read_spectrum(str(file))