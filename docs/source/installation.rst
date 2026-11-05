Installation
============

The ``spectralib`` library (spectrum I/O, broadening, comparison metrics, plotting) is
pure Python and runs on Linux, macOS and Windows. Python 3.12 or newer is
required. The dataset itself is part of the repository and is **not installed** with the library.

Option 1: conda / Anaconda (recommended on Windows)
---------------------------------------------------

Install `Miniforge <https://conda-forge.org/download/>`__ (or use an existing
Anaconda installation), then from a clone of this repository:

.. code-block:: bash

   conda env create -f environment.yml
   conda activate spectralib

Without a terminal, in **Anaconda Navigator**: *Environments* → *Import* →
select ``environment.yml`` → *Import*, then launch a notebook in the ``spectralib``
environment. ``environment.yml`` uses the ``conda-forge`` channel only.

The environment also contains ``pytest`` (to validate the dataset, see :doc:`testing`), JupyterLab and ``git``,
which pip needs to fetch `tcgm-unitkit <https://gitlab.git.nrw/rwth-bannwarthlab/tcgm-unitkit>`__.

Option 2: pip, library only
---------------------------

.. code-block:: bash

   pip install git+https://gitlab.git.nrw/rwth-bannwarthlab/cpl50.git

Add extras as needed:

.. code-block:: bash

   pip install "spectralib[plot] @ git+https://gitlab.git.nrw/rwth-bannwarthlab/cpl50.git"         # matplotlib
   pip install "spectralib[fingerprint] @ git+https://gitlab.git.nrw/rwth-bannwarthlab/cpl50.git"  # MolBar/Open Babel

Option 3: from a clone, for development
---------------------------------------

.. code-block:: bash

   git clone https://gitlab.git.nrw/rwth-bannwarthlab/cpl50.git
   cd cpl50
   pip install -e ".[dev]"

With `uv <https://docs.astral.sh/uv/>`__ instead, ``uv sync --all-extras`` builds the
environment and fetches a matching Python interpreter on any platform.

Platform support
----------------

.. list-table::
   :header-rows: 1
   :widths: 55 15 15 15

   * - Component
     - Linux
     - macOS
     - Windows
   * - library, dataset, plotting
     - ✔
     - ✔
     - ✔
   * - ``comp_fingerprints`` (MolBar, Open Babel)
     - ✔
     - ✔
     - —

.. note:: 
   MolBar v1.2.0 publishes no Windows wheel, so ``pip install "spectralib[fingerprint]"`` installs without it on Windows and the fingerprint tests skip there. Everything else, including the full dataset validation, runs on all three platforms.
