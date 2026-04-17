import pytest
from cpl50.io import _validate_header, REQUIRED_FIELDS

valid_header = "10.3390/molecules23102606,FL1-C1,0,0,0,0,di,0"
invalid_header = "0,FL1-C1,293.15,5e-5,meoh,255,di,0"
invalid_header2 = "10.3390/molecules23102606,FL1-C1,293.15,5e-5,abc,255,di,0"

def test_missing_doi_fails():
    
    parts = [p.strip() for p in invalid_header.strip().split(",")]
    hdict = dict(zip(REQUIRED_FIELDS, parts))

    with pytest.raises(ValueError):
        _validate_header(hdict)


def test_invalid_solvent():
    parts = [p.strip() for p in invalid_header2.strip().split(",")]
    hdict = dict(zip(REQUIRED_FIELDS, parts))

    with pytest.raises(ValueError):
        _validate_header(hdict)


def test_zero_fields_allowed():
    parts = [p.strip() for p in valid_header.strip().split(",")]
    hdict = dict(zip(REQUIRED_FIELDS, parts))

    hdict["file"] = "test.csv"

    _validate_header(hdict)

    assert hdict["T"] == "0"
    assert hdict["c"] == "0"
    assert hdict["solv"] == "0"
