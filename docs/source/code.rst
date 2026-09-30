Module Documentation
=====================

This section contains automated documentation as deduced from the source code. This is meant as rough guidance to ease understanding of some of the code structure. Some additional information might be found here, that are not contained in other parts of the documentation.

Every module below links to its own page, which carries the documentation of the individual classes and functions.

Spectrum
--------

The ``Spectrum`` container (x, y, unit, header metadata): unit conversion (optionally with Jacobian), shift, crop,
normalisation and interpolation.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.spectrum

Units
-----

Prefactors for :math:`\varepsilon` and :math:`\Delta\varepsilon` from the ``tcgm_unitkit`` constants,
:math:`f \rightarrow D` and :math:`g = 4R/D`.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.units

Broadening
----------

Gaussian/Lorentzian broadening (FWHM), ensemble averaging of sticks, :math:`\varepsilon` and :math:`\Delta\varepsilon`
spectra and emission profiles.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.broadening

Metrics
-------

Cosine similarity, lobe-resolved cosines, :math:`E_\mathrm{spe}`, :math:`E_\mathrm{ene}`, optimal shift, main-band
sign and ``benchmark``.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.metrics

IO / Parsing
------------

Dataset parsers and header validation, dataset summaries, ``.CHRG``/``.UHF`` readers.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.io

Utilities
---------

Header registries (required fields, DOI pattern, accepted solvents), solvent canonicalisation and Kabsch RMSD.

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.utils

Plotting
--------

Matplotlib helpers (optional dependency).

.. autosummary::
   :toctree: _generated/
   :recursive:
   :nosignatures:

   cpl50.plotting
