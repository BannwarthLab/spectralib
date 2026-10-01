"""Compute MolBar and InChI fingerprints for .xyz structures.

For every <stem>.xyz found, <stem>.molbar and <stem>.inchi are written next to it.
Total charge and unpaired electrons are read from xtb-style .CHRG / .UHF files in the
same folder (default 0 / 0). A descriptor file is only (over)written if its computation succeeded.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from importlib.metadata import version
from pathlib import Path

from joblib import Parallel, cpu_count, delayed
from molbar.barcode import CalculationError, get_molbar_from_file
from openbabel import pybel

_TTY = sys.stdout.isatty()
OK = "\033[92m[ OK ]\033[0m" if _TTY else "[ OK ]"
FAIL = "\033[91m[FAIL]\033[0m" if _TTY else "[FAIL]"


def _natural_key(path: Path) -> list:
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.as_posix())]


def find_xyz(target: Path) -> list[Path]:
    """Return ``target`` if it is a file, else all .xyz files below it in natural order."""
    return [target] if target.is_file() else sorted(target.rglob("*.xyz"), key=_natural_key)


def read_charge_uhf(xyz: Path) -> tuple[int, int]:
    """Read total charge and unpaired electrons from .CHRG / .UHF next to ``xyz``."""
    chrg, uhf = xyz.parent / ".CHRG", xyz.parent / ".UHF"
    return (int(chrg.read_text()) if chrg.is_file() else 0, int(uhf.read_text()) if uhf.is_file() else 0)


def fingerprint(xyz: Path) -> tuple[Path, str, dict[str, str], dict[str, str]]:
    """Compute MolBar and InChI for one structure. Returns (xyz, state, results, errors)."""
    pybel.ob.obErrorLog.StopLogging()  # failures are reported via the return value
    try:
        charge, uhf = read_charge_uhf(xyz)
    except ValueError as e:
        return xyz, "", {}, {".CHRG/.UHF": str(e)}

    results, errors = {}, {}
    try:
        results["molbar"] = get_molbar_from_file(
            str(xyz), total_charge=charge, multiplicity=uhf + 1, log_file=os.devnull, no_console=True
        )
    except CalculationError as e:
        errors["molbar"] = str(e).rsplit(": ", 1)[-1]  # strip molbar's nested 'failed for <path>' prefixes
    mol = next(pybel.readfile("xyz", str(xyz)), None)
    inchi = mol.write("inchi").strip() if mol else ""
    if inchi.startswith("InChI="):
        results["inchi"] = inchi
    else:
        errors["inchi"] = "Open Babel could not generate an InChI"
    return xyz, f"charge={charge:+d} uhf={uhf}", results, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", type=Path, help=".xyz file or directory (searched recursively)")
    parser.add_argument(
        "-j", "--threads", type=int, default=1, help="structures processed in parallel (default: 1, -1: all available cores)"
    )
    args = parser.parse_args(argv)

    target = args.target.resolve()
    files = find_xyz(target) if target.exists() else []
    if not files:
        print(f"{FAIL} no .xyz files found at {target}", file=sys.stderr)
        return 2

    root = target.parent if target.is_file() else target
    n, width = len(files), max(len(str(f.relative_to(root))) for f in files)
    threads = cpu_count() if args.threads == -1 else args.threads
    print(f"MolBar {version('molbar')} | Open Babel {pybel.ob.OBReleaseVersion()} | {threads} worker(s)")
    print(f"Scanning {target}: {n} .xyz file(s)\n")

    failed: dict[Path, dict[str, str]] = {}
    jobs = Parallel(n_jobs=threads, return_as="generator_unordered")(delayed(fingerprint)(f) for f in files)
    for i, (xyz, state, results, errors) in enumerate(jobs, 1):
        for kind, value in results.items():
            xyz.with_suffix(f".{kind}").write_text(value + "\n")
        head = f"[{i:>{len(str(n))}}/{n}] {FAIL if errors else OK} {xyz.relative_to(root)!s:<{width}}"
        if errors:
            failed[xyz] = errors
        print(head, "; ".join(f"{k}: {v}" for k, v in errors.items()) if errors else state, sep="  ")

    print(f"\nSummary: {n - len(failed)}/{n} passed, {len(failed)} failed")
    for xyz in sorted(failed, key=_natural_key):
        print(f"  {FAIL} {xyz.relative_to(root)} ({', '.join(failed[xyz])})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
