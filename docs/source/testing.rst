Tests for Data Consistency
==========================

``spectralib`` contains some tests to automatically check the formatting of all files in the dataset. These tests check for:

- a malformed header
- an unknown solvent
- a wrong/unknown unit of the spectral quantity
- a misnamed file
- a missing molecular structure
- a DOI without an entry in ``spectralib.bib``

Furthermore, there are tests checking for duplicate structures, enantiomers of structures already in the dataset, and identifiers (MolBar, InChI) that no longer match the structure provided in a subdirectory.

.. warning::
  The tests cannot check whether the data matches the referenced article. This has to be checked manually by the maintainer/reviewers of merge requests.

The tests run automatically in GitLab's CI/CD pipeline (continuous integration / continuous deployment): every push to the repository, including the branch of a merge request, starts a pipeline that installs ``spectralib`` in a fresh container and runs the full test suite. 

The test suite has two parts (dataset and library tests), which can be selected with the markers ``dataset`` and ``library``. The extent of these tests is explained in the following.

----

Dataset tests
-------------

The dataset tests will check all files stored in ``data/``.

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Test file
     - Scope of tests
   * - ``test_io.py``
     - Every spectrum file is parsable: exactly 8 header fields, DOI present and well-formatted, ``T``, ``c`` positive or ``0``, ``irrad`` :math:`\geq` 100 nm or ``0``, ``solv`` is a known solvent, ``quant``/``unit`` allowed for the file type (LUM or CPL), exactly two columns for spectrum data with strictly increasing wavelength.
   * - ``test_solvents.py``
     - Every solvent used resolves to a dielectric constant and refractive index of the Minnesota Solvent Descriptor
       Database (data provided in ``tcgm-unitkit``).
   * - ``test_structures.py``
     - Every ``.xyz`` file is parsable: atom count derived from all atoms matches the number of atoms declared in the first line, valid element symbols, no NaN/inf coordinates. File names match ``<id>[labels].xyz``. No duplicate structures (same composition and RMSD < 0.1 Å). No two structures whose MolBar is identical or show a mirrored chirality spectrum (duplicates or enantiomers).
   * - ``test_consistency.py``
     - The DOI of every spectrum file has an entry in ``spectralib.bib``, spectra and structures have the same system folders (``<id>/``), spectrum file names follow ``<id>[labels]_<LUM|CPL>[_<int>].csv``, every molecule of a spectrum has an ``.xyz`` file and every ``.xyz`` file belongs to a spectrum.
   * - ``test_fingerprints.py``
     - Recompute MolBar (from ``.xyz`` file and associated ``.CHRG``/``.UHF``) and InChI (from ``.xyz`` file alone) for every structure and check that it equals the stored ``.molbar`` and ``.inchi`` files. 

.. note::
  ``test_fingerprints.py`` needs the ``fingerprint`` optional dependencies installed and is available for Linux/macOS but not for Windows at the moment.

----

Library tests
-------------

The library tests check the code of ``spectralib`` but do not check the data consistency for files stored under ``data/``. However, some of the tests use files from ``data/`` as input.

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Test file
     - Scope of tests
   * - ``test_broadening.py``
     - Normalization of lineshape functions, width conversions, broadening.
   * - ``test_metrics.py``
     - Tests different metrics to compare two spectra (e.g. simulated vs experimental).
   * - ``test_spectrum.py``, ``test_io.py``, ``test_solvents.py``
     - Jacobian, normalization, interpolation, unit conversion, IO related to parsing header, solvent names.
   * - ``test_plotting.py``, ``test_summarize_spectra.py``
     - Comparison plot of two different spectra (e.g. simulated vs experimental), checks ``summarize_spectra`` command on real and invalid files.

----

Running the tests
-----------------

With an environment from :ref:`usage:Installation`, you can just use:

.. code-block:: bash

   pytest tests -v                      # everything
   pytest tests -v -m dataset           # dataset tests only
   pytest tests -v -m library           # library tests only

To check only some spectra, without pytest, ``summarize_spectra`` prints information as a table and reports invalid files:

.. code-block:: bash

   summarize_spectra data/spectra/44            # one system
   summarize_spectra --select 9 44 -c file solv # selected systems and columns

----

Continuous integration
----------------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Pipeline
     - Jobs
   * - GitLab (``.gitlab/.gitlab-ci.yml``)
     - Apptainer images (Rocky Linux 10, Python 3.12–3.14): ``ruff``, ``mypy``, ``pytest`` with coverage, documentation built and published to GitLab Pages.
   * - `GitHub mirror <https://github.com/BannwarthLab/spectralib>`__ (``.github/workflows/tests.yml``)
     - pip and conda installs on Linux, macOS and Windows, fingerprint tests, building and installing the wheel.
