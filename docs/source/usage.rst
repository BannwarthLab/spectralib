spectralib Python Library
=========================

Alongside the dataset stored under ``data/``, ``spectralib`` contains some Python code to read and validate the data in this repo, and to compare different spectra. 
The installation of ``spectralib`` described in the following is only needed for these tasks and to run the tests (:doc:`testing`).

----

Installation
------------

The ``spectralib`` library is written in Python and runs on Linux, macOS and Windows. Python 3.12 or newer is required.

Option 1: conda / Anaconda (recommended on Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install `Miniforge <https://conda-forge.org/download/>`__ (or use an existing
Anaconda installation). Then get a copy of the repository, either with ``git``:

.. code-block:: bash

   git clone https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git
   cd spectralib

or, without ``git``, by downloading it from `GitLab <https://gitlab.git.nrw/rwth-bannwarthlab/spectralib>`__ (*Code* → *Download source code* → *zip*) and unpacking it. In the repository folder, create and activate the
environment:

.. code-block:: bash

   conda env create -f environment.yml
   conda activate spectralib

This also installs ``spectralib`` itself from the repository folder (``pip install -e .`` in ``environment.yml``).

Without a terminal, in **Anaconda Navigator**: *Environments* → *Import* → select ``environment.yml`` → *Import*, then launch a notebook in the ``spectralib`` environment. ``environment.yml`` uses the ``conda-forge`` channel only.

The environment also contains ``pytest`` (to validate the dataset, see :doc:`testing`), JupyterLab and ``git``, which pip needs to fetch `tcgm-unitkit <https://gitlab.git.nrw/rwth-bannwarthlab/tcgm-unitkit>`__.

Option 2: pip, library only
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install git+https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git

Add extras as needed:

.. code-block:: bash

   pip install "spectralib[plot] @ git+https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git"         # matplotlib
   pip install "spectralib[fingerprint] @ git+https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git"  # MolBar/Open Babel

Option 3: from a clone, for development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git
   cd spectralib
   pip install -e ".[dev]"

With `uv <https://docs.astral.sh/uv/>`__ instead, ``uv sync --all-extras`` builds the environment and fetches a matching Python interpreter on any platform.

Platform support
~~~~~~~~~~~~~~~~

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
   MolBar v1.2.0 publishes no Windows wheel, so ``pip install "spectralib[fingerprint]"`` installs without it on Windows and the fingerprint tests skip there. 

----

Modules
-------

The modules of ``spectralib`` are:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Module
     - Content
   * - :mod:`~spectralib.spectrum`
     - ``Spectrum`` class (x, y, unit, header metadata) featuring unit conversion, shifting, normalisation, interpolation
   * - :mod:`~spectralib.broadening`
     - Gaussian/Lorentzian broadening (FWHM) of stick spectra, emission profiles with :math:`E^3` weighting
   * - :mod:`~spectralib.metrics`
     - Cosine similarity, lobe-resolved cosines, optimal shift, main-band sign, peak position, collected in the ``benchmark`` function
   * - :mod:`~spectralib.io`
     - Read/write spectra (with header validation) and structures, ``.CHRG``/``.UHF``
   * - :mod:`~spectralib.dataset`
     - Metadata of all spectra, dataset summary, queries (solvents, filters)
   * - :mod:`~spectralib.plotting`
     - Matplotlib helpers (``pip install -e ".[plot]"``)
   * - :mod:`~spectralib.utils`
     - Header registries (required fields, DOI pattern, accepted solvents), solvent canonicalisation, structure alignment and RMSD calculation

The full documentation is given in :ref:`usage:API Reference`.

----

Example
-------

.. code-block:: python

   import numpy as np

   from spectralib import read_spectrum
   from spectralib.broadening import emission_spectrum
   from spectralib.metrics import benchmark

   # excited-state data from a calculation
   e = np.array([2.80])     # emission energy, eV
   f = np.array([0.05])     # oscillator strength, dimensionless
   r = np.array([-12.0])    # rotatory strength, 1e-40 esu^2 cm^2

   # dipole strength D = |mu|^2 in units of R:
   # D = 3 f / (2 E) in atomic units (E in Eh, D in e^2 a0^2), 1 e^2 a0^2 = 64604.75e-40 esu^2 cm^2
   d = 3 * f / (2 * e / 27.211386) * 64604.75   # 1e-40 esu^2 cm^2, here 47089
   g_lum = 4 * r / d                            # dissymmetry factor, here -1.02e-3

   # emission profiles with E^3 weighting:
   # I = I_L + I_R ~ D and Delta I = I_L - I_R ~ 2R, so that 2 Delta I / I = 4R/D = g_lum
   grid = np.linspace(1.5, 6.0, 2000)   # eV
   lum = emission_spectrum(e, d, grid, fwhm=0.35)
   cpl = emission_spectrum(e, 2 * r, grid, fwhm=0.35)

   exp_lum = read_spectrum("data/spectra/12/12_LUM.csv").convert_x("ev", jacobian=True)
   exp_cpl = read_spectrum("data/spectra/12/12_CPL.csv").convert_x("ev", jacobian=True)
   res_lum = benchmark(exp_lum, lum, signed=False)
   res_cpl = benchmark(exp_cpl, cpl, signed=True, shift=res_lum["shift"])

``benchmark`` returns a dictionary. For the CPL comparison above, this would read:

.. code-block:: python

   >>> res_cpl
   {'peak_error': 0.038,        # eV, E_peak(calc) - E_peak(ref) before the shift
    'shift': -0.053,            # eV, added to the calculated energies (here taken from res_lum)
    'cosine': 0.711,            # signed cosine similarity at that shift
    'o_pos': 0.0,               # cosine of the positive lobes (the calculated spectrum has none)
    'o_neg': 0.712,             # cosine of the negative lobes
    'signs_match': True,        # the lobe with the larger area has the same sign in both spectra
    'sign_ratio_ref': -0.993,   # (A+ - A-) / (A+ + A-) of the reference
    'sign_ratio_calc': -1.0}    # the same for the calculated spectrum within the measured window

For unsigned spectra (``signed=False``) only the first three keys are returned, here
``res_lum = {'peak_error': 0.097, 'shift': -0.053, 'cosine': 0.905}``. The technical notes below explain how each
value is obtained.

.. admonition:: Technical Notes on Comparing Spectra

   1. **Energy axis and Jacobian.** Unless the article states otherwise, spectral data usually refers to intensities per wavelength interval, :math:`I(\lambda)` with :math:`\lambda` in nm. The intensity per energy interval is :math:`I(E) = I(\lambda)\,|\mathrm{d}\lambda/\mathrm{d}E| \propto \lambda^2 I(\lambda)` :cite:`mooneyGetBasicsRight2013`. ``convert_x("ev", jacobian=True)`` applies the :math:`\lambda^2` factor. Ratios such as :math:`g_\mathrm{lum} = 2\Delta I/I` and quantities that are not densities (:math:`\varepsilon`, :math:`\Delta\varepsilon`) should be converted to energy units without it (``jacobian=False``). The calculated counterpart is the number of photons emitted per energy interval (spontaneous emission): :math:`I = I_\mathrm{L} + I_\mathrm{R} \propto E^3 D` with the dipole strength :math:`D = |\mu|^2`, and :math:`\Delta I = I_\mathrm{L} - I_\mathrm{R} \propto E^3 \cdot 2R`, each multiplied with the lineshape, so that :math:`g_\mathrm{lum} = 2\Delta I/I = 4R/D`. ``emission_spectrum()`` applies the :math:`E^3` factor, and the example shows how :math:`D` is obtained from :math:`f` in the units of :math:`R`. ``spectrum()`` broadens the sticks without any prefactor. For a single Gaussian band (FWHM 0.35 eV at 2.8 eV) the :math:`E^3` factor moves the maximum by about 0.02 eV to higher energies.

   2. **Normalisation.** Experimental intensities are given in arbitrary units (``i``, ``di``, mdeg) and depend on concentration and instrument settings, so only band shapes and signs can be compared. The cosine similarity is invariant to scaling, so ``benchmark`` needs no normalisation. For plots, you should normalise with ``normalize("max")`` (:math:`\max|y| = 1`). For noisy data, the CPL maximum often corresponds to a noise spike, so smooth the data first (``smooth(spec, fwhm=0.05)`` from :mod:`~spectralib.metrics`) or use ``normalize("area")``.

   3. **Energy shift.** ``optimal_shift`` scans energy shifts between the calculated and the reference spectrum within ``bounds`` (default ±1 eV, step 5 meV, with parabolic refinement of the optimum). This shift is added to the calculated energies. For CPL, the shift derived from the LUM spectrum of the same system (``shift=res_lum["shift"]`` in the example) can be taken. If no shift is passed, ``benchmark`` aligns signed spectra on :math:`|y|` (``objective="abs_cosine"``), which ignores the sign, so that a sign error cannot be hidden by shifting a band onto a lobe of the matching sign.

   4. **Main-band sign.** ``signs_match`` compares the sign of the lobe with the larger area (:math:`A_+` or :math:`A_-`). The calculated spectrum is evaluated within the measured window after the shift. ``sign_ratio_ref`` and ``sign_ratio_calc`` :math:`=(A_+-A_-)/(A_++A_-)` show how well-defined this sign is: :math:`\pm 1` for a single band, near 0 if the positive and negative lobes have similar areas.

   5. **Band shape.** ``cosine`` :math:`= \int a\,b\,\mathrm{d}E \big/ \sqrt{\int a^2\,\mathrm{d}E \int b^2\,\mathrm{d}E}` at the chosen shift (1 identical, 0 no overlap, −1 mirror image). For CPL, ``o_pos`` and ``o_neg`` are the cosines of the positive and of the negative parts separately: ``nan`` if the lobe is absent in both spectra, 0 if it is absent in one of them (e.g. a calculated single band compared to an experimental spectrum with lobes of both signs).

   6. **Peak energy.** ``peak_error`` :math:`= E_\mathrm{peak}(\mathrm{calc}) - E_\mathrm{peak}(\mathrm{ref})` before any shift, taken at the extremum of the dominant-sign lobe. The reference is smoothed (``smooth_fwhm=0.05`` eV) to avoid noise spikes, and the calculated spectrum is restricted to the range that ``bounds`` can shift into the measured window.

.. note::
   The comparison metrics and their recommended use will be discussed in the publication associated with ``spectralib`` (see :doc:`citation`). Until then, the functions in :mod:`~spectralib.metrics`, their defaults and the keys returned by ``benchmark`` may still change.

----

API Reference
-------------

Documentation generated from the source code. 

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   spectralib.spectrum
   spectralib.broadening
   spectralib.metrics
   spectralib.io
   spectralib.dataset
   spectralib.utils
   spectralib.plotting
