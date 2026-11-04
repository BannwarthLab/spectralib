# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

sys.path.insert(0, str(ROOT / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# Authors and version are taken from pyproject.toml, so they are maintained in one place.

with open(ROOT / "pyproject.toml", "rb") as f:
    _meta = tomllib.load(f)["project"]

project = "spectralib"
author = ", ".join(a["name"] for a in _meta["authors"])
version = release = str(_meta["version"])


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip


def write_solvent_table() -> None:
    """Render the accepted solvents (``spectralib.utils``) as an rST table for ``dataset.rst``."""
    from spectralib.utils import DIELECTRIC_CONSTANTS, SOLVENT_ALIASES

    rows = [
        "   * - ``{}``\n     - {}\n     - {}".format(alias, name, DIELECTRIC_CONSTANTS.get(name, "-"))
        for alias, name in sorted(SOLVENT_ALIASES.items(), key=lambda kv: (kv[1], kv[0]))
    ]
    table = [
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 25 45 30",
        "",
        "   * - ``solv``",
        "     - Solvent",
        "     - Dielectric constant",
        *rows,
        "",
    ]
    out = HERE / "_generated" / "solvents.inc"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(table), encoding="utf-8")


def setup(app):
    app.connect("autodoc-skip-member", skip)
    write_solvent_table()


autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx_rtd_theme",
    "sphinxcontrib.bibtex",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "special.rst"]

autosummary_generate = True

bibtex_bibfiles = ["lit.bib", "spectralib.bib"]
bibtex_default_style = "unsrt"

# Render "Attributes:" sections as :ivar: fields of the class instead of separate
# `.. attribute::` objects. Without this, every attribute described in a class docstring is
# also documented by autodoc itself (undoc-members is on), which Sphinx reports as a duplicate
# object description.
napoleon_use_ivar = True

# Prefix autosectionlabel targets with their document name, so that identically named sections
# in different files (e.g. an "Installation" heading in two pages) do not collide.
autosectionlabel_prefix_document = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["hack.css", "custom.css"]

with open(os.path.join(os.path.dirname(__file__), "special.rst"), encoding="utf-8") as special_file:
    rst_prolog = "\n" + special_file.read() + "\n"

latex_elements = {
    "preamble": r"""
\usepackage[titles]{tocloft}
\usepackage{amsmath}
""",
}
latex_show_urls = "footnote"
