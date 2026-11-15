"""Print the header information of spectra as a table and report files that do not pass validation.

Every .csv file found is read with the same header and data checks as the dataset tests
(spectralib.io.read_spectrum). The exit status is 1 if any file is invalid, so the command can be
used to check new files before opening a merge request, e.g.

    summarize_spectra data/spectra/53
"""

from __future__ import annotations

import argparse
from pathlib import Path

from spectralib.dataset import load_dataset_metadata, summarize_dataset

COLUMNS = ["file", "mol", "doi", "T", "c", "solv", "irrad", "quant", "unit"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("data/spectra")],
        help=".csv files or directories (searched recursively); default: data/spectra",
    )
    parser.add_argument("-s", "--select", type=int, nargs="+", metavar="ID", help="only these system IDs")
    parser.add_argument(
        "-c", "--columns", nargs="+", choices=COLUMNS, default=COLUMNS, metavar="COL", help=f"columns, of: {COLUMNS}"
    )
    args = parser.parse_args(argv)

    records = []
    for path in args.paths:
        if not path.exists():
            parser.error(f"{path} does not exist")
        records += load_dataset_metadata(path, select=args.select)
    if not records:
        parser.error("no .csv files found")

    summarize_dataset(records, columns=args.columns)
    return 1 if any("error" in r for r in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
