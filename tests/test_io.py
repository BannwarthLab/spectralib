# =============================================================================
# test_io.py
# =============================================================================
from pathlib import Path

import pytest

from cpl50.io import REQUIRED_FIELDS, _validate_header, read_spectrum, summarize_dataset

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_header(raw: str, file_tag: str = "test.csv") -> dict:
    parts = [p.strip() for p in raw.strip().split(",")]
    hdict = dict(zip(REQUIRED_FIELDS, parts))
    hdict["file"] = file_tag
    return hdict


# solv is now required — use a real solvent in the valid baseline
VALID_RAW    = "10.3390/molecules23102606,FL1-C1,0,0,meoh,0,di,0"
INVALID_DOI  = "0,FL1-C1,293.15,5e-5,meoh,255,di,0"
INVALID_SOLV = "10.3390/molecules23102606,FL1-C1,293.15,5e-5,abc,255,di,0"


@pytest.fixture
def valid_header():
    return _make_header(VALID_RAW)


# ---------------------------------------------------------------------------
# DOI
# ---------------------------------------------------------------------------

def test_missing_doi_raises():
    with pytest.raises(ValueError, match="DOI"):
        _validate_header(_make_header(INVALID_DOI))

def test_zero_doi_raises(valid_header):
    valid_header["DOI"] = "0"
    with pytest.raises(ValueError, match="DOI"):
        _validate_header(valid_header)

def test_malformed_doi_raises(valid_header):
    valid_header["DOI"] = "not-a-doi"
    with pytest.raises(ValueError, match="DOI"):
        _validate_header(valid_header)

# ---------------------------------------------------------------------------
# Sentinel fields (T, c, irrad are optional; solv is required)
# ---------------------------------------------------------------------------

def test_optional_sentinels_allowed(valid_header):
    """T, c, and irrad may be '0'; solv must always be a known solvent."""
    _validate_header(valid_header)
    assert valid_header["T"]     == "0"
    assert valid_header["c"]     == "0"
    assert valid_header["irrad"] == "0"

def test_zero_solvent_raises(valid_header):
    """'0' is not a valid solvent — solvent is always required."""
    valid_header["solv"] = "0"
    with pytest.raises(ValueError, match="[Ss]olvent"):
        _validate_header(valid_header)

def test_unknown_solvent_raises():
    with pytest.raises(ValueError, match="[Ss]olvent"):
        _validate_header(_make_header(INVALID_SOLV))

def test_negative_temperature_raises(valid_header):
    valid_header["T"] = "-10.0"
    with pytest.raises(ValueError, match="[Tt]emperature"):
        _validate_header(valid_header)

def test_zero_temperature_raises(valid_header):
    valid_header["T"] = "0.0"
    with pytest.raises(ValueError, match="[Tt]emperature"):
        _validate_header(valid_header)

def test_negative_concentration_raises(valid_header):
    valid_header["c"] = "-1e-5"
    with pytest.raises(ValueError, match="[Cc]oncentration"):
        _validate_header(valid_header)

def test_irrad_below_100_raises(valid_header):
    valid_header["irrad"] = "50"
    with pytest.raises(ValueError, match="[Ii]rrad"):
        _validate_header(valid_header)

# ---------------------------------------------------------------------------
# File-type / quantity / unit consistency
# ---------------------------------------------------------------------------

def test_invalid_cpl_quantity_raises(valid_header):
    valid_header["file"] = "33a_CPL.csv"
    valid_header["quant"] = "not_a_quantity"
    with pytest.raises(ValueError, match="[Qq]uant"):
        _validate_header(valid_header)

def test_invalid_lum_unit_raises(valid_header):
    valid_header["file"] = "33a_LUM.csv"
    valid_header["unit"] = "not_a_unit"
    with pytest.raises(ValueError, match="[Uu]nit"):
        _validate_header(valid_header)

@pytest.mark.parametrize("fname", [
    "33a_CPL.csv",
    "33ab_CPL.csv",
    "1_CPL_1.csv",
    "1_CPL_2.csv",
])
def test_cpl_filename_variants_route_correctly(valid_header, fname):
    valid_header["file"] = fname
    valid_header["quant"] = "not_valid"
    with pytest.raises(ValueError, match="CPL"):
        _validate_header(valid_header)

@pytest.mark.parametrize("fname", [
    "33a_LUM.csv",
    "33ab_LUM.csv",
    "1_LUM_1.csv",
])
def test_lum_filename_variants_route_correctly(valid_header, fname):
    valid_header["file"] = fname
    valid_header["unit"] = "not_valid"
    with pytest.raises(ValueError, match="LUM"):
        _validate_header(valid_header)

# ---------------------------------------------------------------------------
# Integration: parse all real spectra
# ---------------------------------------------------------------------------

def test_all_spectra_parse():
    base = Path("data/spectra")
    csv_files = list(base.rglob("*.csv"))
    assert csv_files, "No .csv files found under data/spectra"
    for file in csv_files:
        read_spectrum(str(file))

# ---------------------------------------------------------------------------
# summarize_dataset
# ---------------------------------------------------------------------------

def test_summary_contains_molecule_name(tmp_path, capsys):
    content = "10.3390/molecules23102606,mol,293.15,1e-5,meoh,250,di,0\n0,1\n1,2\n"
    d = tmp_path / "spectra"
    d.mkdir()
    (d / "a_LUM.csv").write_text(content)
    summarize_dataset(str(d))
    assert "mol" in capsys.readouterr().out

def test_summary_reports_errors_not_raises(tmp_path, capsys):
    (tmp_path / "bad.csv").write_text("this,is,not,a,valid,header,at,all\n")
    summarize_dataset(str(tmp_path))
    out = capsys.readouterr().out
    assert "ERROR" in out
    assert "bad.csv" in out

def test_summary_sentinel_displayed_as_dash(tmp_path, capsys):
    content = "10.3390/molecules23102606,mol,0,0,meoh,0,di,0\n0,1\n1,2\n"
    d = tmp_path / "spectra"
    d.mkdir()
    (d / "a_LUM.csv").write_text(content)
    summarize_dataset(str(d))
    assert " - " in capsys.readouterr().out

def test_summary_empty_directory(tmp_path, capsys):
    summarize_dataset(str(tmp_path))
    assert "0 file(s)" in capsys.readouterr().out