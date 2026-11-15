# =============================================================================
# test_summarize_spectra.py  –  the summarize_spectra command
# =============================================================================
from importlib.metadata import entry_points

from conftest import DATA

from spectralib.scripts.summarize_spectra import main


def test_console_script_registered():
    eps = entry_points(group="console_scripts", name="summarize_spectra")
    assert eps, "summarize_spectra not registered, reinstall spectralib"
    assert next(iter(eps)).load() is main


def test_dataset_summary_passes(capsys):
    assert main([str(DATA / "spectra"), "--select", "9", "44"]) == 0
    out = capsys.readouterr().out
    assert "44_LUM_1.csv" in out
    assert "0 error(s)" in out


def test_invalid_file_fails(tmp_path, capsys):
    bad = tmp_path / "1_LUM.csv"
    bad.write_text("10.1021/x,mol,293.15,0,unobtainium,0,I,0\n400,1\n401,2\n")
    assert main([str(bad)]) == 1
    assert "Invalid solvent" in capsys.readouterr().out
