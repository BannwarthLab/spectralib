"""Shared fixtures for the test suite.

The benchmark dataset lives in the repository, not inside the installed
package, so dataset paths are anchored to the repository root instead of the
current working directory.
"""

from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Root of the benchmark dataset shipped in the repository."""
    return DATA
