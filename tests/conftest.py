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


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test that is not a dataset test as a library test.

    Dataset tests (format and consistency of data/) carry the ``dataset`` marker explicitly;
    everything else tests the code of spectralib. Select with ``-m dataset`` or ``-m library``.
    """
    for item in items:
        if item.get_closest_marker("dataset") is None:
            item.add_marker(pytest.mark.library)
