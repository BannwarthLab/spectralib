# =============================================================================
# test_fingerprints.py  –  MolBar / InChI references in data/structures are reproducible
# =============================================================================
import os
import shutil
import sys
from importlib.metadata import entry_points

import pytest
from conftest import DATA

try:
    from spectralib.scripts.compute_fingerprints import main
except ImportError:  # 'fingerprint' extra not installed; never skip silently in CI
    # MolBar publishes no Windows wheel, so the extra is incomplete there by design.
    if os.environ.get("CI") and sys.platform != "win32":
        raise
    pytest.skip("requires spectralib[fingerprint] (unavailable on Windows)", allow_module_level=True)

DATA_DIR = DATA / "structures"
XYZ = sorted(DATA_DIR.rglob("*.xyz"))
KINDS = ("molbar", "inchi")

# the references under test live in the dataset
pytestmark = pytest.mark.dataset


def test_console_script_registered():
    eps = entry_points(group="console_scripts", name="comp_fingerprints")
    assert eps, "comp_fingerprints not registered, reinstall spectralib"
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
