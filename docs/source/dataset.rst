File Description
================

Each ``.csv`` file contains a 1-line header with information about the experiments in the format:

``DOI,molname,T,c,solv,irrad,quant,unit``

with:

- ``DOI``: The doi to the article the data was extracted from or presented in.

- ``molname``: A short description/alias of the respective molecule, typically one that is given in the
  corresponding article.

- ``T``: The temperature (in K) at which the measurements were performed.
  If none was given/found, ``0`` is added here. "Room temperature" refers to 293.15 K.

- ``c``: The concentration (in M) at which the measurements were performed.
  If none was given/found, ``0`` is added here.

- ``solv``: A (short) name of the solvent used in the experiments.
  A list of accepted solvents may be found in ``src/spectralib/utils.py`` and :ref:`below <dataset:Accepted Solvents>`.

- ``irrad``: The used irradiation wavelength (in nm).
  If none was given/found, ``0`` is added here.

- ``quant``: The experimental quantity measured, e.g. ``di`` (:math:`\Delta I`) in CPF.

- ``unit``: The unit of ``quant``, if provided.
  If none was given/found, or the quantity is dimensionless, ``0`` is added here.

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

- Molecular geometries:

  .. code-block:: text

     <natoms>
     <comment line>
     <element1> <x1> <y1> <z1>
     <element2> <x2> <y2> <z2>
     ...

All geometries are optimized with the
`semiempirical electronic structure theory method GFN2-xTB <https://pubs.acs.org/doi/10.1021/acs.jctc.8b01176>`__
as implemented in the `xtb program <https://github.com/grimme-lab/xtb>`__ (version 6.7.0):
``xtb coord.xyz --opt (--chrg <int> --uhf <int>)``

If molecules are charged or have unpaired electrons in their electronic ground states, this information is contained
in the ``.CHRG`` and ``.UHF`` files.

Further Notes
-------------

- Measurements in thin films, matrices, or gels are omitted and deliberately excluded from the dataset at the moment.
- Some geometries were simplified (truncation of flexible alkane chains, tBu -> Me, etc.) to be computationally more
  tractable, and may differ from the Lewis structures illustrated in :doc:`data`.

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

Generated from ``SOLVENT_ALIASES`` in ``src/spectralib/utils.py``; a new solvent is added there (and its dielectric
constant to ``DIELECTRIC_CONSTANTS``).

.. include:: _generated/solvents.inc
