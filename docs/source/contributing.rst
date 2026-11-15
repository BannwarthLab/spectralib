How to Contribute
=================

This chapter contains step-by-step instructions and further details on how you can contribute to ``spectralib``. 

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - To Add
     - Instruction
   * - spectra of a new system
     - Follow the steps below and open a merge request in the `spectralib GitLab <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/merge_requests>`_.
   * - spectra of a known system under other measurement conditions
     - Add ``<id>_LUM_<int>.csv`` / ``<id>_CPL_<int>.csv`` to the existing folder (see :doc:`dataset`). 
   * - Report or correct data
     - Open an `issue <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/issues>`_ or a `merge request <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/merge_requests>`_ with the fix.
   * - a solvent that is not accepted yet
     - Add its aliases to ``SOLVENT_ALIASES`` (see :ref:`Solvents <dataset:Further Notes>`).

.. tip::
   If you are not familiar with working with git, we welcome you to contribute anyway! To do so, just open an `issue <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/issues>`_ stating your concern + the files and the DOI of interest, and we will try to add the data for you.

Adding a new system
-------------------

.. list-table::
   :header-rows: 1
   :widths: 6 50 44

   * - #
     - Step
     - Checked in the CI/CD pipeline by
   * - 1
     - Take the next free system number ``<id>`` and create ``data/spectra/<id>/`` and ``data/structures/<id>/``.
     - ``test_consistency.py``
   * - 2
     - Add ``<id>_LUM.csv`` and/or ``<id>_CPL.csv`` with the format explained in :doc:`dataset`.
     - ``test_io.py``, ``test_solvents.py``
   * - 3
     - Provide the ``<id>.xyz`` file. If multiple molecules constitute the system, add alphabetic labels (e.g. ``<id>a.xyz``). Add ``.CHRG``/``.UHF`` files to declare the molecular charge and number of unpaired electrons, if different from zero. :sup:`A,B`

     - ``test_structures.py``
   * - 4
     - Compute the molecular identifiers (``comp_fingerprints data/structures/<id>``). :sup:`C`
     - ``test_fingerprints.py``
   * - 5
     - Add the BibTeX entry of the article (with ``doi`` entry) to ``docs/source/spectralib.bib``.
     - ``test_consistency.py``, documentation build
   * - 6
     - Check your files with ``summarize_spectra data/spectra/<id>`` (header table, errors per file), run
       ``pytest tests -m dataset`` and open a merge request. In its description, state where the values come from (e.g. raw data from the authors, or digitised from a figure).
     - GitLab pipeline

:sup:`A` Ideally structures should be optimized with GFN2-xTB (xtb 6.7.0). If this is not possible, please try to provide at least some structural information even in different file formats (e.g. crystal structures in ``.cif``). 

:sup:`B` If the structure was simplified relative to the article, add the system to ``TRUNCATED`` in ``docs/source/_ext/autotables.py``.

:sup:`C` This step needs ``pip install -e ".[fingerprint]"`` and is currently possible only on Linux/macOS, but not Windows due to the MolBar installation.  

----

Contributing code
-----------------

``spectralib`` is deliberately small. Changes to the library should come with tests and pass ``ruff check``, ``ruff format --check`` and ``mypy`` (configured in ``pyproject.toml``). These can be installed as ``pip install -e ".[dev]"``.

.. _license:

License
-------

The data in ``data/`` are distributed under `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`__
(``data/LICENSE``), the code under the BSD-3-Clause license (``LICENSE``). By opening a merge request you agree that
your contribution is distributed under these licenses.
