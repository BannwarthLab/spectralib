File Description
================

Each ``.csv`` file contains a one-line header with information about the experiments in the format

``DOI,molname,T,c,solv,irrad,quant,unit``

with:

.. list-table::
   :header-rows: 1
   :widths: 16 50 14 20

   * - Field
     - Description
     - Unit
     - If not reported
   * - ``DOI``
     - Digital object identifier (DOI) of the article the data refers to.
     - --
     - required
   * - ``molname``
     - Short name/alias of the molecule, typically the one given in the corresponding article.
     - --
     - required
   * - ``T``
     - Temperature of the measurement. "Room temperature" refers to 293.15 K.
     - K
     - ``0``
   * - ``c``
     - Concentration of the sample measured.
     - M (mol/L)
     - ``0``
   * - ``solv``
     - Short name of the solvent (see also :ref:`Solvents <dataset:Further Notes>`).
     - --
     - required
   * - ``irrad``
     - Irradiation wavelength.
     - nm
     - ``0``
   * - ``quant``
     - Measured quantity, e.g. ``di`` (:math:`\Delta I`) in CPL (allowed values below).
     - --
     - required
   * - ``unit``
     - Unit of ``quant`` (allowed values below).
     - --
     - ``0`` (also if dimensionless)

A valid example header looks like this:

``10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0``

This refers to the CPL spectrum of FL1-C1 from `this article <https://doi.org/10.3390/molecules23102606>`_, measured at room temperature (293.15 K) with a concentration of 5e-5 M in MeOH using :math:`\lambda_\mathrm{irr} = 255~\mathrm{nm}`. The reported intensity is a :math:`\Delta I`.

Equally valid (still passing the tests) would be the reduced form containing only the required attributes explained in the table above:

``10.3390/molecules23102606,FL1-C1,0,0,meoh,0,di,0``

The following values of ``quant`` and ``unit`` are accepted (``VALID_QUANT_*`` and ``VALID_UNIT_*`` in ``src/spectralib/utils.py``):

.. list-table::
   :header-rows: 1
   :widths: 16 54 30

   * - File
     - ``quant``
     - ``unit``
   * - ``*_LUM.csv``
     - ``i`` (intensity), ``dc`` (DC channel of the detector, total intensity)
     - ``0``, ``v``
   * - ``*_CPL.csv``
     - ``di`` (:math:`\Delta I`), ``cpl``, ``cpf``, ``glum`` (:math:`g_\mathrm{lum}`)
     - ``0``, ``mdeg``

----

Data Format
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Content
   * - ``<id>_LUM.csv``, ``<id>_CPL.csv``
     - Header line (see above) followed by one data point per line consisting of ``<wavelength in nm>,<quant>``. Wavelengths must be strictly increasing, intensities are given in the units reported in the corresponding article (typically arbitrary units).
   * - ``<id>.xyz``
     - Standard xyz file format with coordinates in Å: ``<number of atoms>`` followed by a comment line, then ``<element> <x> <y> <z>`` per atom.
   * - ``.CHRG``, ``.UHF``
     - Total charge of the molecule and number of unpaired electrons. These files are only present next to the ``.xyz`` files, if these quantities would be different from zero.
   * - ``<id>.molbar``, ``<id>.inchi``
     - `MolBar <https://doi.org/10.1039/D4DD00208C>`_ and InChI
       (Open Babel) of the structure, written by the commandline tool ``comp_fingerprints``. MolBar uses the total charge and number of unpaired electrons from ``.CHRG``/``.UHF``. InChI is generated from the xyz file alone.

Example of a ``*_CPL.csv``:

.. code-block:: text

   10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0
   <wavelength1>,<quant1>
   <wavelength2>,<quant2>
   ...

.. note::
  All files contain plain text, so it is not necessary - but certainly possible - to use  ``spectralib`` to parse them. You can also use your own parsers, if you like. 


Example of a coordinate ``*.xyz`` file:

.. code-block:: text

  29
  energy: -39.268067357794 gnorm: 0.000486333281 xtb: 6.7.0 (75e6a61)
  C           -8.40649192775876        1.68111665797931        0.16790412714097
  C           -7.40325377397034        0.74441830406762       -0.01615535729277
  C           -6.12850027281151        1.13830848581499       -0.44750559826571
   ...

.. note:: 
  As of version |release|, all geometries are optimized with the semiempirical electronic structure theory method `GFN2-xTB <https://pubs.acs.org/doi/10.1021/acs.jctc.8b01176>`__ as implemented in the `xtb program <https://github.com/grimme-lab/xtb>`__ (version 6.7.0):

  ``xtb coord.xyz --opt (--chrg <int> --uhf <int>)``

----

File Names
----------

Every system added to this database receives one folder in ``data/spectra`` and ``data/structures`` with a new ``<id>``.
Systems composed of multiple molecules (e.g. noncovalent complexes) carry alphabetic labels, e.g.:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - Content
   * - ``spectra/41/41a_LUM.csv``
     - luminescence spectrum of ``structures/41/41a.xyz``
   * - ``spectra/41/41ab_CPL.csv``
     - CPL spectrum of the noncovalent complex of ``41a.xyz`` and ``41b.xyz``

If a system is measured at different experimental conditions, further files carry integer suffixes ``_<int>``, e.g. ``44_LUM.csv`` (toluene, 293.15 K) and ``44_LUM_1.csv`` (toluene, 77 K) in ``data/spectra/44``. 
The full pattern for filenames therefore reads

``<id>[labels]_<LUM|CPL>[_<int>].csv``

and the presence of all referenced structures is checked by ``tests/test_consistency.py``.

----

Further Notes
-------------

.. important::
  Measurements in thin films, matrices or gels are deliberately omitted from the dataset at the moment (version |release|). If you feel this data should be included, please reach out to the maintainers of this repository.

.. warning::
  Some geometries were simplified (truncation of flexible alkane chains, tBu replaced with Me, etc.) to be computationally more tractable, and may differ from the structures illustrated in the original article. These systems are marked in the table in :doc:`data`.


**Solvents**

The solvent field declared in the one-line header (``solv``) is compared with the names given in ``SOLVENT_ALIASES`` in ``src/spectralib/utils.py``. If you have to add a solvent or alias, which is not yet covered by this list, create new entries to ``SOLVENT_ALIASES``. This could read as follows:

.. code-block:: python

  SOLVENT_ALIASES = MappingProxyType(
  {
  # methanol
  "methanol": "methanol",
  "meoh": "methanol",
  "ch3oh": "methanol",
  ...
  })

where we just added different trivial names for methanol. The value on which all aliases agree should follow the names declared in `tcgm-unitkit <https://gitlab.git.nrw/rwth-bannwarthlab/tcgm-unitkit>`_ (module ``unitkit.constants.solvents``). This data is taken from the Minnesota Solvent Descriptor Database (`mnsddb.pdf <https://comp.chem.umn.edu/solvation/mnsddb.pdf>`_) to have a proper source for a solvent's dielectric constants (``DIELECTRIC_CONSTANTS``) and refractive indices (``REFRACTIVE_INDICES``), which are relevant parameters for simulating LUM and CPL spectra. 

The following table lists all accepted solvents with aliases, and the dielectric constants and refractive indices.

.. include:: _generated/solvents.inc

.. note::
    This table is automatically generated from ``SOLVENT_ALIASES`` in ``src/spectralib/utils.py`` and the solvent data of ``tcgm-unitkit`` when the documentation is built (``docs/source/_ext/autotables.py``). Further aliases should be added to ``SOLVENT_ALIASES``.
