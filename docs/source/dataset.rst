File Description
================

Each ``.csv`` file contains a 1-line header with information about the experiments in the format:

``DOI,molname,T,c,solv,irrad,quant,unit``

with:

.. list-table::
   :header-rows: 1
   :widths: 16 52 12 20

   * - Field
     - Meaning
     - Unit
     - If not reported
   * - ``DOI``
     - DOI of the article the data was extracted from or presented in.
     - --
     - required
   * - ``molname``
     - Short description/alias of the molecule, typically the one given in the corresponding article.
     - --
     - required
   * - ``T``
     - Temperature of the measurement. "Room temperature" refers to 293.15 K.
     - K
     - ``0``
   * - ``c``
     - Concentration of the measurement.
     - M
     - ``0``
   * - ``solv``
     - Short name of the solvent, see :ref:`Accepted Solvents <dataset:Accepted Solvents>` (also
       ``src/spectralib/utils.py``).
     - --
     - required
   * - ``irrad``
     - Irradiation wavelength.
     - nm
     - ``0``
   * - ``quant``
     - Measured quantity, e.g. ``di`` (:math:`\Delta I`) in CPF.
     - --
     - required
   * - ``unit``
     - Unit of ``quant``.
     - --
     - ``0`` (also if dimensionless)

A valid example header, e.g., for molecule 9 (``data/spectra/9/9_CPL.csv``) looks like this:

``10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0``

This refers to the CPL spectrum of FL1-C1 from `this article <https://doi.org/10.3390/molecules23102606>`__,
measured at room temperature (293.15 K) with a concentration of 5e-5 M in MeOH using
:math:`\lambda_\mathrm{irr} = 255~\mathrm{nm}`. The reported intensity is a :math:`\Delta I`.

Data Format
-----------

- CPL spectra:

  .. code-block:: text

     <header>
     <wavelength1>, <quant1>
     <wavelength2>, <quant2>
     ...

- Molecular geometries (with coordinates in Angstrom):

  .. code-block:: text

     <natoms>
     <comment line>
     <element1> <x1> <y1> <z1>
     <element2> <x2> <y2> <z2>
     ...

All geometries are optimized with the
semiempirical electronic structure theory method `GFN2-xTB <https://pubs.acs.org/doi/10.1021/acs.jctc.8b01176>`__
as implemented in the `xtb program <https://github.com/grimme-lab/xtb>`__ (version 6.7.0):
``xtb coord.xyz --opt (--chrg <int> --uhf <int>)``

If molecules are charged or have unpaired electrons in their electronic ground states, this information is contained
in the ``.CHRG`` and ``.UHF`` files.

Further Notes
-------------

- Measurements in thin films, matrices or gels are omitted and deliberately excluded from the dataset at the moment (project version |version|).
- Some geometries were simplified (truncation of flexible alkane chains, tBu -> Me, etc.) to be computationally more
  tractable, and may differ from the Lewis structures illustrated in the original article. This is declared in the table in :doc:`data`.

File Names
----------

Systems with more than one molecule carry alphabetic labels. One example is system 33, where we find:

- ``33a_LUM.csv``, the luminescence spectrum of ``structures/33a.xyz``
- ``33ab_CPL.csv``, the CPL spectrum of a noncovalent complex of ``33a.xyz`` and ``33b.xyz``

If data for systems measured at different experimental conditions is added, these carry integer suffixes ``_<int>``.
An example is provided in ``data/spectra/25``:

- ``25_LUM.csv`` - measurement in toluene at 293.15 K
- ``25_LUM_1.csv`` - measurement in toluene at 77 K

etc.

Accepted Solvents
-----------------

Generated from ``SOLVENT_ALIASES`` in ``src/spectralib/utils.py``. A new solvent should be added there with its dielectric constant ( ``DIELECTRIC_CONSTANTS``).
The dielectric constants are taken from `https://comp.chem.umn.edu/solvation/mnsddb.pdf <https://comp.chem.umn.edu/solvation/mnsddb.pdf>`_

.. include:: _generated/solvents.inc
