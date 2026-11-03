pystda Documentation
=========================

.. code-block:: text

                    _      _
    _ __  _   _ ___| |_ __| | __ _
   | '_ \| | | / __| __/ _` |/ _` |
   | |_) | |_| \__ \ || (_| | (_| |
   | .__/ \__, |___/\__\__,_|\__,_|
   |_|    |___/

**pystda** is a Python-based implementation of simplified time-dependent quantum chemical (sQC) methods.

A rough overview of the modular components of the code is provided below.

.. image:: ../../imgs/module_overview.png

The ground-state reference calculation can be carried out with an external program and passed to **pystda** as a molden file.
Alternatively, a ground-state calculation based on a provided geometry (keyword `geom`) can be performed via **pyscf**.

Currently, we support a variety of different methods:

* TDA and TD-DFT
* sTDA :cite:`grimmeSimplifiedTammDancoffDensity2013a` and sTD-DFT :cite:`bannwarthSimplifiedTimedependentDensity2014a`, their exact-integral variants (XsTDA, XsTD-DFT) :cite:`dewergifosseEXactIntegralSimplified2024b` and the RI-based TDA-ris, TDDFT-ris (``tda-ri``/``tddft-ri``) :cite:`zhouMinimalAuxiliaryBasis2023b`
* hole-hole TDA (based on an N+2 reference or an N electron FON reference) :cite:`yuInitioNonadiabaticMolecular2020b,bannwarthHoleHoleTamm2020b` and particle-particle TDA[:red:`Add WT Ref`]

``pystda`` provides a dense (full) solver to compute optical spectra across broad energy ranges or a iterative solver to compute a selected number of excited-states.
Both solvers support different configuration selection techniques:
* MO window - Set an energy window for active MOs 
* PT2 - Configuration selection as carried out in sTDA (see :cite:`grimmeSimplifiedTammDancoffDensity2013a`). Divides configurations into primary, secondary, or neglected.
* Ktrunc - Reduces 'active' MOs in the exchange integrals (ij|ab) and (ib|ja) by an explicit cutoff (:red:`ZZ precond paper`)

A run is configured on the command line, through a TOML input file, or both -- see
:doc:`usage`.

.. code-block:: console

   $ pystda --method stddft --geom coord.xyz --basis def2-svp --fct pbe0 --ethr 7.0
   $ plotter stddft.dat --FWHM 0.2

.. Definition of TOC
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage

   data

   examples

   code

   references

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
