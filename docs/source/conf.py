from __future__ import annotations

import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE / "_ext"))  # local extensions for automated documentation based on repo content

# Authors and version taken from pyproject.toml
with open(ROOT / "pyproject.toml", "rb") as f:
    _meta = tomllib.load(f)["project"]

project = "spectralib"
author = ", ".join(a["name"] for a in _meta["authors"])
version = release = str(_meta["version"])


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
    "myst_parser",  # CHANGELOG.md in changelog.rst
    "autotables",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True

bibtex_bibfiles = ["lit.bib", "spectralib.bib"]
bibtex_default_style = "unsrt"

napoleon_use_ivar = True
autosectionlabel_prefix_document = True

# Fmt html
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "../../imgs/spectralib_logo.svg"
html_favicon = "_static/favicon.png"
html_title = f"spectralib {release}"
html_theme_options = {
    "logo_only": True,
    "style_nav_header_background": "#ffffff",
    "collapse_navigation": False,
    "navigation_depth": 3,
}
html_show_sourcelink = False

latex_elements = {
    "preamble": r"""
\usepackage[titles]{tocloft}
\usepackage{amsmath}
""",
}
latex_show_urls = "footnote"
