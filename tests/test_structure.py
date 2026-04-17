from pathlib import Path

from cpl50.io import read_xyz


def test_read_all_structure_files():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data" / "structures"

    xyz_files = sorted(data_dir.rglob("*.xyz"))
    assert xyz_files, "No .xyz structure files found in data/structures"

    for xyz_file in xyz_files:
        elements, coords = read_xyz(str(xyz_file))
        assert len(elements) > 0, f"No elements parsed from {xyz_file}"
        assert coords.shape[0] == len(elements), f"Coordinate count mismatch in {xyz_file}"
        assert coords.shape[1] == 3, f"Coordinates in {xyz_file} should have 3 columns"
