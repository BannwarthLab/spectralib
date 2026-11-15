Acknowledgments
===============

The dataset and ``spectralib`` build on the following software and data. If you use the corresponding part, please cite it as well.

.. list-table::
   :header-rows: 1
   :widths: 24 40 36

   * - Software / data
     - Used for
     - Reference
   * - `xtb <https://github.com/grimme-lab/xtb>`__ (GFN2-xTB)
     - optimisation of all geometries (xtb 6.7.0)
     - :cite:`bannwarthGFN2xTB2019,bannwarthExtendedTightbindingQuantum2021`
   * - `MolBar <https://gitlab.git.nrw/rwth-bannwarthlab/molbar>`__
     - molecular identifier (``.molbar``)
     - :cite:`molbar2024`
   * - `Open Babel <https://openbabel.org>`_, `InChI <https://www.inchi-trust.org/>`__
     - molecular identifier (``.inchi``)
     - :cite:`hellerInChIIUPACInternational2015, oboyleOpenBabelOpen2011`
   * - `Minnesota Solvent Descriptor Database <https://comp.chem.umn.edu/solvation/mnsddb.pdf>`__
     - dielectric constants and refractive indices of the solvents
     - :cite:`wingetMinnesotaSolventDescriptor1999`
   * - `tcgm-unitkit <https://gitlab.git.nrw/rwth-bannwarthlab/tcgm-unitkit>`__
     - physical constants, unit conversion, solvent data in ``spectralib``
     - --
   * - NumPy, SciPy
     - numerics in ``spectralib``
     - :cite:`harrisArrayProgrammingNumPy2020,virtanenSciPyFundamentalAlgorithms2020`
   * - Matplotlib
     - plotting in ``spectralib``
     - :cite:`hunterMatplotlib2DGraphics2007`

Parts of the code and documentation were drafted or revised with the help of generative AI (Claude, Anthropic) and reviewed by the authors. The initial code base, research ideas, scientific content and the curation of all data are the authors' own work, and the authors take full responsibility for the content of this repository.

