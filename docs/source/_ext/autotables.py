"""Extension to generate rST tables from the dataset and library.

Each generator below renders one table into ``docs/source/_generated/<name>.inc``. Generators are called with the release string (``release`` in ``conf.py``) and listed in ``GENERATORS``.
"""

from __future__ import annotations

import re
from pathlib import Path

from sphinx.application import Sphinx

HERE = Path(__file__).resolve().parents[1]  # docs/source
ROOT = HERE.parents[1]  # repository root


def write_solvent_table(release: str) -> None:
    """Render the accepted solvents (``spectralib.utils``) as an rST table for ``dataset.rst``."""
    from spectralib.utils import DIELECTRIC_CONSTANTS, REFRACTIVE_INDICES, SOLVENT_ALIASES

    by_name: dict[str, list[str]] = {}
    for alias, name in SOLVENT_ALIASES.items():
        by_name.setdefault(name, []).append(alias)
    rows = [
        "   * - {}\n     - {}\n     - {}\n     - {}".format(
            name,
            ", ".join(f"``{a}``" for a in sorted(aliases)),
            DIELECTRIC_CONSTANTS[name],
            REFRACTIVE_INDICES[name],
        )
        for name, aliases in sorted(by_name.items())
    ]
    table = [
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 26 42 16 16",
        "",
        "   * - Solvent",
        "     - Accepted ``solv`` values",
        "     - :math:`\\varepsilon_r` (298 K)",
        "     - :math:`n_D` (293 K)",
        *rows,
        "",
    ]
    _write("solvents", table)


# -- Overview table of data.rst ----------------------------------------------
# Generated from the spectrum headers: one row per system folder in data/spectra, the molecule
# name from the header (CPL file preferred), the references from the header DOIs via the ``doi``
# field of spectralib.bib, and footnote A where no LUM spectrum exists. Only what the data cannot
# tell is kept here by hand:

# Further references per system, e.g. corrections, as BibTeX keys of spectralib.bib.
EXTRA_REFERENCES: dict[str, list[str]] = {
    "5": ["islaCorrectionBis4aza6helicene2019"],
    "6": ["islaCorrectionBis4aza6helicene2019"],
    "7": ["islaCorrectionBis4aza6helicene2019"],
    "8" : ["fujikiCorrectionFujikiQuestions2018"],
    "9" : ["fujikiCorrectionFujikiQuestions2018"],
    "46" : ["bossonCorrigendumPhysicochemicalElectronic2019"],
}

#: Systems whose geometry was simplified relative to the article (footnote ``B``).
TRUNCATED: set[str] = {"19", "21", "22", "23", "25", "36", "37", "47"}


_RST_SPECIAL = str.maketrans({c: "\\" + c for c in "\\*`|_@"})


def _natural_key(name: str) -> list:
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def write_overview_table(release: str) -> None:
    """Render the systems of the dataset as an rST table for ``data.rst``."""
    from pybtex.database import parse_file

    bib = parse_file(str(HERE / "spectralib.bib"))
    doi_to_key = {e.fields["doi"].strip().lower(): k for k, e in bib.entries.items() if "doi" in e.fields}

    rows = []
    n_lum = n_cpl = 0
    for system in sorted(
        (p for p in (ROOT / "data" / "spectra").iterdir() if p.is_dir()), key=lambda p: _natural_key(p.name)
    ):
        names: dict[str, str] = {}  # molecule label (e.g. 41a, 41ab) -> name, CPL file preferred
        dois: list[str] = []
        has_lum = False
        for csv in sorted(system.glob("*.csv"), key=lambda p: _natural_key(p.name)):
            doi, molname = (field.strip() for field in csv.read_text(encoding="utf-8").splitlines()[0].split(",")[:2])
            label, kind = csv.stem.split("_")[:2]
            has_lum |= kind == "LUM"
            n_lum += kind == "LUM"
            n_cpl += kind == "CPL"
            if kind == "CPL" or label not in names:
                names[label] = molname
            if doi.lower() not in dois:
                dois.append(doi.lower())
        missing = [d for d in dois if d not in doi_to_key]
        if missing:
            raise ValueError(f"DOI(s) {missing} of system {system.name} have no entry in spectralib.bib")
        keys = [doi_to_key[d] for d in dois] + EXTRA_REFERENCES.get(system.name, [])
        marks = ("" if has_lum else "A") + ("B" if system.name in TRUNCATED else "")
        index = system.name + (f"\\ :sup:`{marks}`" if marks else "")
        molecule = " / ".join(names[label].translate(_RST_SPECIAL) for label in sorted(names, key=_natural_key))
        rows.append(f"   * - {index}\n     - {molecule}\n     - :cite:`{','.join(keys)}`")

    _write(
        "overview_summary",
        [
            f"Version |release| of the dataset contains {len(rows)} systems with {n_lum} luminescence and {n_cpl} CPL spectra.",
            "",
        ],
    )
    table = [
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 12 38 50",
        "",
        "   * - Index",
        "     - Molecule",
        "     - Reference",
        *rows,
        "",
    ]
    _write("overview", table)


# -- Growth of the dataset per version ---------------------------------------------------------
# The current version (``release`` in conf.py) is counted
# when the documentation is built; earlier versions are fixed numbers in PAST_VERSIONS.
#
# Prior to a new release, append the counts of the version that is being superseded to PAST_VERSIONS.

PAST_VERSIONS: list[tuple[str, int, int, int]] = [
    ("0.1.0", 12, 13, 12),
]


def _count_current() -> tuple[int, int, int]:
    """(systems, LUM spectra, CPL spectra) in data/spectra of the working tree."""
    files = list((ROOT / "data" / "spectra").glob("*/*.csv"))
    return (
        len({f.parent.name for f in files}),
        sum("_LUM" in f.stem for f in files),
        sum("_CPL" in f.stem for f in files),
    )


def write_growth_plot(release: str) -> None:
    """Plot the number of systems, LUM and CPL spectra per version into ``_generated/dataset_growth.png``."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [*PAST_VERSIONS, (release, *_count_current())]

    x = range(len(rows))
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for i, (label, colour, marker) in enumerate(
        [("Systems", "#00185b", "o"), ("LUM spectra", "#0e5f9b", "s"), ("CPL spectra", "#0aa1ca", "^")], start=1
    ):
        ax.plot(x, [r[i] for r in rows], marker=marker, color=colour, label=label)
    ax.set_xticks(list(x), [r[0] for r in rows])
    ax.set_xlabel("Version number")
    ax.set_ylabel("Number of entries")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    (HERE / "_generated").mkdir(exist_ok=True)
    fig.savefig(HERE / "_generated" / "dataset_growth.png", dpi=200)
    plt.close(fig)


def _write(name: str, lines: list[str]) -> None:
    out = HERE / "_generated" / f"{name}.inc"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


#: Table generators, run in this order at the start of every build.
GENERATORS = [write_solvent_table, write_overview_table, write_growth_plot]


def _generate(app: Sphinx) -> None:
    for generator in GENERATORS:
        generator(app.config.release)


def setup(app: Sphinx) -> dict:
    app.connect("builder-inited", _generate)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
