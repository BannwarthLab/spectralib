Python Library
==============

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Module
     - Content
   * - ``spectrum``
     - ``Spectrum`` (x, y, unit, header metadata): unit conversion (optionally with Jacobian), shift, crop,
       normalisation, interpolation
   * - ``units``
     - Prefactors for :math:`\varepsilon` and :math:`\Delta\varepsilon` from the
       `tcgm-unitkit <https://gitlab.git.nrw/rwth-bannwarthlab/tcgm-unitkit>`__ constants;
       :math:`f\rightarrow D`; :math:`g = 4R/D` (axis conversions use ``unitkit.convert_energy_unit``)
   * - ``broadening``
     - Gaussian, Lorentzian, Voigt and pseudo-Voigt broadening (FWHM), ensemble averaging of sticks, :math:`\varepsilon` and
       :math:`\Delta\varepsilon` in L mol\ :sup:`-1` cm\ :sup:`-1`, emission profiles
   * - ``metrics``
     - Cosine similarity, lobe-resolved cosines, :math:`E_\mathrm{spe}`, :math:`E_\mathrm{ene}`, optimal shift,
       main-band sign, ``benchmark``
   * - ``io``
     - Read/write spectra (with header validation) and structures, ``.CHRG``/``.UHF``
   * - ``dataset``
     - Metadata of all spectra, dataset summary, queries (solvents, filters)
   * - ``plotting``
     - Matplotlib helpers (``pip install -e ".[plot]"``)

The library works on plain arrays (energies in eV, :math:`f`, :math:`R` in :math:`10^{-40}` esu\ :sup:`2` cm\ :sup:`2`).
Quantum-chemistry output is read with `tcgmio <https://gitlab.git.nrw/rwth-bannwarthlab/utils/tcgmio>`__, which is
not a dependency of ``spectralib``.

.. code-block:: python

   import numpy as np
   from unitkit import convert_energy_unit
   from tcgmio.orca import read_orca_opa_spectrum

   from spectralib import read_spectrum
   from spectralib.broadening import delta_epsilon_spectrum, emission_spectrum, epsilon_spectrum
   from spectralib.metrics import benchmark
   from spectralib.units import osc_to_dipole_strength

   grid = np.linspace(1.5, 6.0, 2000)                                   # eV
   _, _, e_cm, f, _ = read_orca_opa_spectrum("orca.out")                # cm-1, dimensionless
   r    = read_orca_opa_spectrum("orca.out", cd=True)[3]                 # 1e-40 esu^2 cm^2
   e    = convert_energy_unit(e_cm, "cm-1", "ev")
   eps  = epsilon_spectrum(e, f, grid, fwhm=0.3)                         # L mol-1 cm-1
   deps = delta_epsilon_spectrum(e, r, grid, fwhm=0.3)                   # L mol-1 cm-1

   # emission at the S1 geometry: LUM ~ E^3 D, CPL ~ E^3 4R  (ratio -> g_lum)
   d1  = osc_to_dipole_strength(e[:1], f[:1])
   lum = emission_spectrum(e[:1], d1, grid, fwhm=0.35)
   cpl = emission_spectrum(e[:1], 4 * r[:1], grid, fwhm=0.35)

   # Voigt line shape: fwhm = (Gaussian FWHM, Lorentzian FWHM); "pseudo_voigt" takes the same tuple
   lum_v = emission_spectrum(e[:1], d1, grid, fwhm=(0.30, 0.10), shape="voigt")

   exp_lum = read_spectrum("data/spectra/12/12_LUM.csv").convert_x("ev", jacobian=True)
   exp_cpl = read_spectrum("data/spectra/12/12_CPL.csv").convert_x("ev", jacobian=True)
   res_lum = benchmark(exp_lum, lum, signed=False)
   res_cpl = benchmark(exp_cpl, cpl, signed=True, shift=res_lum["shift"])

Comparing signed spectra (CPL/ECD)
----------------------------------

1. **Energy axis.** Compare on an energy axis. Experimental LUM/CPL intensities are densities per wavelength
   interval; ``convert_x("ev", jacobian=True)`` multiplies by :math:`\lambda^2`. On this dataset this moves LUM maxima
   by 0.05–0.19 eV (0.54 eV for molecule 7), i.e. by as much as typical method errors. :math:`\varepsilon`,
   :math:`\Delta\varepsilon` and :math:`g_\mathrm{lum}` are not densities and are converted without the Jacobian.
2. **Normalisation.** Experimental CPL is in arbitrary units (:math:`\Delta I`, mdeg), so only shapes can be compared.
   Normalise sign-preserving: ``max`` for plots, ``area`` (:math:`\int|y| = 1`) for metrics, as the peak height depends
   on the broadening width and on noise spikes.
3. **Shift.** Take the shift from the unsigned partner spectrum (LUM for CPL, UV-vis for ECD), since both come from
   the same transitions. Without a partner, align on :math:`|y|` (``objective="abs_cosine"``), so an energy error
   cannot be traded against a sign error.
4. **Main-band sign** (``signs_match``): the sign of the lobe with the larger area, evaluated within the measured
   window. Report ``sign_ratio`` :math:`=(A_+-A_-)/(A_++A_-)` alongside it; a value near 0 means a balanced couplet
   with no well-defined main band. Of the 52 experimental CPL spectra, only ``9_CPL`` has :math:`|\text{ratio}| < 0.5`.
5. **Band shape at that shift.** Signed cosine similarity (1 = identical, −1 = mirror image) and the area-normalised
   :math:`E_\mathrm{spe} = \int|\sigma^\mathrm{ref}-\sigma|\,/\int|\sigma^\mathrm{ref}|` (0 = identical, 2 = mirror
   image or no overlap). The lobe-resolved cosines :math:`(o_+, o_-)` show which lobe fails.
6. **Energies.** ``peak_error`` per molecule (reference smoothed to suppress noise spikes); :math:`E_\mathrm{ene}` =
   RMSD over the dataset. With state-resolved theory-vs-theory data, ``e_ene(..., match=True)`` handles root flipping.

:math:`E_\mathrm{ene}` and :math:`E_\mathrm{spe}` are Eqs. 11–12 of :cite:`zhouMinimalAuxiliaryBasis2023b`.
There they compare two calculated spectra in the same units over :math:`[0, \omega_\mathrm{max}]`; for that case use
``e_spe(..., norm=None, window="union")``.
