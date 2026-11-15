A Dataset for Luminescence and Circularly Polarized Luminescence Spectra
====================================================================================

.. image:: ../../imgs/spectralib_logo.svg
   :alt: spectralib logo
   :width: 320px
   :align: center


This repository collects published experimental luminescence (LUM) and circularly polarized luminescence (CPL) spectroscopic data, together with Cartesian coordinates of the molecular structures.
The one-line header in the ``csv`` files of spectra contains information about the experimental measurement conditions (e.g. solvent, temperature, excitation wavelength) and the DOI of the article the data was published in (see :doc:`dataset`).
Molecular fingerprints (`MolBar <https://doi.org/10.1039/D4DD00208C>`_, `InChI <https://www.inchi-trust.org/>`_) are added for each molecular structure to avoid duplicates across the database and unambiguously assign the enantiomeric species corresponding to the spectroscopic data supplied (see :ref:`Data Format <dataset:Data Format>`).  

``spectralib`` was designed from a theoreticians' point of view with the aim to provide a curated dataset for benchmarking quantum chemical methods for the calculation of LUM and CPL spectra. Related to that, the Python library ``spectralib`` offers some convenient functions for spectral analysis (see :doc:`usage`).

For experimentalists, the database serves as a common point to store and share spectroscopic data, but also compare to other measurements. Overall, the raw data should be made accessible to a broader audience. The chapter :doc:`contributing` explains how to add your data.

The repository is split into two parts:

- Experimental spectroscopic data, Cartesian coordinates and fingerprints of the molecular systems investigated, located under ``data/spectra/<id>`` and ``data/structures/<id>`` (overview of all systems in :doc:`data`)
- The Python library ``spectralib``, which can be used to read, analyze, plot and validate the data, located under ``src/spectralib`` (:doc:`usage`)


Further notes:

.. list-table::
   :header-rows: 0
   :widths: 22 78

   * - Traceable sources
     - Every spectrum ``csv`` file contains the DOI of the article the data was published in. :doc:`data` lists all molecular systems available in the current version of ``spectralib`` with their literature source. The :doc:`testing` check that every DOI has an entry in the bibliography file ``spectralib.bib``.
   * - File formats
     - Spectroscopic data is provided as comma-separated text (wavelength in nm, spectral intensity may differ between files and spectrum type). Cartesian coordinates are given as xyz files (``<id>.xyz``, coordinates in Å). Molecular fingerprints are written as plain text files (``<id>.inchi, <id>.molbar``). Molecular charges and the number of unpaired electrons are given as plain text files (``.CHRG, .UHF``). Data contained in the one-line header are explained in detail in :doc:`dataset`. The :doc:`testing` recompute the identifiers and compare molecular structures to avoid duplicates in the database.
   * - Extendability
     - The data format is checked in the CI/CD pipeline (see :doc:`testing`) to identify formal errors automatically. This simplifies the contributing process and maintenance.
   * - Versioning
     - The git history tracks all changes made in the repository, and every release (current version: |release|) is tagged in git. If you use data from this repository, you can simply cite the tagged version you used (see :doc:`citation`).
   * - Licensing
     - The data is licensed under CC BY 4.0, the code under BSD-3-Clause (see :ref:`license`).

The source code and the dataset are hosted at `gitlab.git.nrw/rwth-bannwarthlab/spectralib
<https://gitlab.git.nrw/rwth-bannwarthlab/spectralib>`__.

----

Quick Start 
-----------

Below you find brief instructions how to clone the repository and access its content with Python. More details about other functionality is explained in the chapter :doc:`usage`.

.. code-block:: bash

   git clone https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git
   cd spectralib
   conda env create -f environment.yml
   conda activate spectralib

.. code-block:: python

   from spectralib import read_spectrum
   from spectralib.dataset import summarize_dataset
   from spectralib.plotting import plot_spectrum

   summarize_dataset("data/spectra")                  # all spectra with their header information
   spec = read_spectrum("data/spectra/9/9_CPL.csv")   # x in nm, y in the unit of spec.metadata
   print(spec.metadata["molname"], spec.metadata["DOI"])
   plot_spectrum(spec)                                # wavelength axis as in the file

----

Contributing
-----------------

We encourage **you** to complement and extend this dataset! Just add new data in the appropriate format, `add an issue/work item <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/issues>`_ describing what you added, and create `a merge request via GitLab <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/merge_requests>`_. 
Alternatively, you can also just create an issue pointing someone else toward the reference data that may be still missing. 
``spectralib`` uses a CI/CD pipeline to run tests on the added files to ensure that the data maintains the correct format. 
See :doc:`contributing` for the step-by-step guide.



.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   Home <self>
   data
   dataset
   testing
   usage
   contributing
   citation
   acknowledgments
   funding
   changelog
   references