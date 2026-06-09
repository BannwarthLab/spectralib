# =============================================================================
# test_io_orca.py
# =============================================================================
from pathlib import Path

import pytest

from cpl50.io_orca import read_absorption, read_cd


@pytest.fixture
def orca_file():
    """Path to test ORCA output file."""
    return Path(__file__).parent / "tmp_orca.out"


# ---------------------------------------------------------------------------
# read_absorption
# ---------------------------------------------------------------------------

def test_absorption_file_exists(orca_file):
    """Verify test file is available."""
    assert orca_file.exists(), f"Test file not found: {orca_file}"


def test_absorption_returns_tuple(orca_file):
    """read_absorption returns a 4-tuple."""
    result = read_absorption(str(orca_file))
    assert isinstance(result, tuple)
    assert len(result) == 4


def test_absorption_returns_lists(orca_file):
    """read_absorption returns four lists."""
    e_ev, e_nm, f_len, f_vel = read_absorption(str(orca_file))
    assert isinstance(e_ev, list)
    assert isinstance(e_nm, list)
    assert isinstance(f_len, list)
    assert isinstance(f_vel, list)


def test_absorption_lists_same_length(orca_file):
    """All four return lists have the same length."""
    e_ev, e_nm, f_len, f_vel = read_absorption(str(orca_file))
    n = len(e_ev)
    assert len(e_nm) == n
    assert len(f_len) == n
    assert len(f_vel) == n
    assert n > 0, "No transitions found"


def test_absorption_values_positive(orca_file):
    """Wavelengths and oscillator strengths are positive."""
    e_ev, e_nm, f_len, f_vel = read_absorption(str(orca_file))
    
    assert all(eev > 0 for eev in e_ev), "Some eV values are not positive"
    assert all(enm > 0 for enm in e_nm), "Some nm values are not positive"
    assert all(fl >= 0 for fl in f_len), "Some length fosc values are negative"
    assert all(fv >= 0 for fv in f_vel), "Some velocity fosc values are negative"


def test_absorption_energy_wavelength_relationship(orca_file):
    """eV and nm are inversely related (hc constant)."""
    e_ev, e_nm, _, _ = read_absorption(str(orca_file))
    
    from cpl50.utils import NM_TO_EV_CM
    
    for eev, enm in zip(e_ev, e_nm):
        # Check approximate relationship: E(eV) * lambda(nm) ≈ hc
        product = eev * enm
        expected = NM_TO_EV_CM
        # Allow 0.1% tolerance for rounding
        assert abs(product - expected) / expected < 0.001, \
            f"Energy-wavelength mismatch: {eev} eV * {enm} nm = {product}, expected ~{expected}"


def test_absorption_first_transition(orca_file):
    """Check properties of first transition."""
    e_ev, e_nm, f_len, f_vel = read_absorption(str(orca_file))
    
    # First transition should be 0-1A -> 1-1A: 3.396117 eV, 365.1 nm
    assert len(e_ev) > 0
    assert abs(e_ev[0] - 3.396117) < 0.001
    assert abs(e_nm[0] - 365.1) < 0.1
    assert abs(f_len[0] - 0.002364) < 0.0001


def test_absorption_sufficient_data(orca_file):
    """Verify we extract a reasonable number of transitions."""
    e_ev, e_nm, f_len, f_vel = read_absorption(str(orca_file))
    # ORCA file should have many transitions; check for at least 10
    assert len(e_ev) >= 10, f"Too few transitions: {len(e_ev)}"


# ---------------------------------------------------------------------------
# read_cd
# ---------------------------------------------------------------------------

def test_cd_returns_tuple(orca_file):
    """read_cd returns a 4-tuple."""
    result = read_cd(str(orca_file), transition_index=0)
    assert isinstance(result, tuple)
    assert len(result) == 4


def test_cd_first_transition(orca_file):
    """Check properties of first CD transition."""
    e_ev, e_nm, r_len, r_vel = read_cd(str(orca_file), transition_index=0)
    
    # First transition: 3.396117 eV, 365.1 nm, R(len)=-0.18183, R(vel) should exist
    assert abs(e_ev - 3.396117) < 0.001
    assert abs(e_nm - 365.1) < 0.1
    assert abs(r_len - (-0.18183)) < 0.01


def test_cd_multiple_transitions(orca_file):
    """read_cd can access different transitions."""
    # Get first few transitions
    for idx in range(3):
        e_ev, e_nm, r_len, r_vel = read_cd(str(orca_file), transition_index=idx)
        assert e_ev > 0
        assert e_nm > 0
        assert isinstance(r_len, float)
        assert isinstance(r_vel, float)


def test_cd_positive_energy(orca_file):
    """CD transition energies are positive."""
    for idx in range(5):
        e_ev, e_nm, r_len, r_vel = read_cd(str(orca_file), transition_index=idx)
        assert e_ev > 0, f"Transition {idx} has non-positive eV"
        assert e_nm > 0, f"Transition {idx} has non-positive nm"


def test_cd_energy_wavelength_consistent(orca_file):
    """CD energies and wavelengths follow hc relationship."""
    from cpl50.utils import NM_TO_EV_CM
    
    e_ev, e_nm, r_len, r_vel = read_cd(str(orca_file), transition_index=0)
    
    product = e_ev * e_nm
    expected = NM_TO_EV_CM
    # Allow 0.1% tolerance
    assert abs(product - expected) / expected < 0.001


def test_cd_invalid_index_raises(orca_file):
    """read_cd raises ValueError for invalid transition index."""
    with pytest.raises(ValueError, match="not found"):
        read_cd(str(orca_file), transition_index=9999)


def test_cd_consistency_with_absorption(orca_file):
    """CD transitions should correspond to absorption transitions."""
    abs_e_ev, abs_e_nm, _, _ = read_absorption(str(orca_file))
    
    # Check first few CD transitions match absorption
    for idx in range(min(5, len(abs_e_ev))):
        cd_e_ev, cd_e_nm, _, _ = read_cd(str(orca_file), transition_index=idx)
        assert abs(cd_e_ev - abs_e_ev[idx]) < 0.001, \
            f"Transition {idx}: CD eV={cd_e_ev} vs Absorption eV={abs_e_ev[idx]}"
        assert abs(cd_e_nm - abs_e_nm[idx]) < 0.1, \
            f"Transition {idx}: CD nm={cd_e_nm} vs Absorption nm={abs_e_nm[idx]}"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_read_absorption_missing_file():
    """read_absorption raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        read_absorption("/nonexistent/path/file.out")


def test_read_cd_missing_file():
    """read_cd raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        read_cd("/nonexistent/path/file.out")
