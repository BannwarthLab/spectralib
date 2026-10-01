# =============================================================================
# test_fingerprints.py  –  MolBar / InChI references in data/structures are reproducible
# =============================================================================
import os
import shutil
from importlib.metadata import entry_points
from pathlib import Path

import pytest

try:
    from cpl50.scripts.compute_fingerprints import main
except ImportError:  # 'fingerprint' extra not installed; never skip silently in CI
    if os.environ.get("CI"):
        raise
    pytest.skip("requires cpl50[fingerprint]", allow_module_level=True)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "structures"
XYZ = sorted(DATA_DIR.rglob("*.xyz"))
KINDS = ("molbar", "inchi")


def test_console_script_registered():
    eps = entry_points(group="console_scripts", name="comp_fingerprints")
    assert eps, "comp_fingerprints not registered, reinstall cpl50"
    assert next(iter(eps)).load() is main


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory):
    """Copy data/structures without references and regenerate them with the script."""
    out = tmp_path_factory.mktemp("structures")
    shutil.copytree(DATA_DIR, out, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*(f"*.{k}" for k in KINDS)))
    main([str(out), "--threads", "-1"])
    return out


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("xyz", XYZ, ids=lambda p: p.stem)
def test_fingerprint_matches_reference(regenerated, xyz, kind):
    ref = xyz.with_suffix(f".{kind}")
    new = regenerated / ref.relative_to(DATA_DIR)
    assert ref.is_file(), f"missing reference {ref.relative_to(DATA_DIR)}"
    assert new.is_file(), f"compute_fingerprints failed for {xyz.relative_to(DATA_DIR)} (see captured stdout)"
    assert new.read_text() == ref.read_text()
