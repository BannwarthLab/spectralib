# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from __future__ import annotations

import os
import sys
import tomllib

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "pystda"
author = "Laurence Brandon, Mike Pauls, Anton Rikus, and Christoph Bannwarth"


def get_version_from_toml() -> str:
    """Return the version defined in :file:`pyproject.toml`."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return str(data["project"]["version"])


version = release = get_version_from_toml()


def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)

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

bibtex_bibfiles = ["lit.bib", "cpl50.bib"]
bibtex_default_style = "unsrt"

# Render "Attributes:" sections as :ivar: fields of the class instead of separate
# `.. attribute::` objects. Without this, every attribute described in a class docstring is
# also documented by autodoc itself (undoc-members is on), which Sphinx reports as a duplicate
# object description.
napoleon_use_ivar = True

# Prefix autosectionlabel targets with their document name, so that identically named sections
# in different files (e.g. an "Installation" heading in two pages) do not collide.
autosectionlabel_prefix_document = True

#bibtex_bibfiles = ['lit.bib']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["hack.css"]

with open(os.path.join(os.path.dirname(__file__), "special.rst"), encoding="utf-8") as special_file:
    rst_prolog = "\n" + special_file.read() + "\n"

latex_elements = {
    "preamble": r"""
\usepackage[titles]{tocloft}
\usepackage{amsmath}
""",
}
latex_show_urls = "footnote"
