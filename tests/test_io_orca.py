# =============================================================================
# test_io_orca.py
# =============================================================================
from pathlib import Path

import numpy as np
import pytest

from cpl50.io_orca import read_orca_tddft
from cpl50.units import convert_x

ORCA = Path(__file__).parent / "tmp_orca.out"


@pytest.fixture(scope="module")
def tab():
    return read_orca_tddft(ORCA)


def test_all_tables_present(tab):
    assert set(tab) == {"energy", "f_len", "f_vel", "r_len", "r_vel"}
    assert all(len(v) == 20 for v in tab.values())


def test_first_and_last_rows(tab):
    assert tab["energy"][0] == pytest.approx(3.396117)
    assert tab["f_len"][0] == pytest.approx(0.002364012)
    assert tab["f_vel"][0] == pytest.approx(0.002442011)
    assert tab["r_len"][0] == pytest.approx(-0.18183)
    assert tab["r_vel"][-1] == pytest.approx(7.85182)
    assert tab["r_len"][14] == pytest.approx(-328.07688)


def test_energies_increase(tab):
    assert np.all(np.diff(tab["energy"]) > 0)


def test_orca5_row_format(tmp_path):
    txt = (
        "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS\n"
        "-----\n State   Energy    Wavelength  fosc  T2  TX  TY  TZ\n"
        "         (cm-1)   (nm)                   (au**2)    (au)   (au)   (au)\n-----\n"
        "   1   27391.5    365.1   0.002364012   0.02841  -0.16796   0.00028   0.01421\n"
        "   2   28744.4    347.9   0.001099891   0.01260  -0.00401   0.11217  -0.00002\n\n"
    )
    f = tmp_path / "o5.out"
    f.write_text(txt)
    tab = read_orca_tddft(f)
    assert tab["f_len"] == pytest.approx([0.002364012, 0.001099891])
    assert tab["energy"] == pytest.approx(convert_x(np.array([27391.5, 28744.4]), "cm-1", "ev"))


def test_last_block_wins(tmp_path):
    body = ORCA.read_text()
    f = tmp_path / "two.out"
    f.write_text(body.replace("0.002364012", "0.999999999") + body)
    assert read_orca_tddft(f)["f_len"][0] == pytest.approx(0.002364012)


def test_missing_table_raises(tmp_path):
    f = tmp_path / "empty.out"
    f.write_text("nothing here\n")
    with pytest.raises(ValueError, match="No TDDFT"):
        read_orca_tddft(f)
