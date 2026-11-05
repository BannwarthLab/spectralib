Running Tests
=============

The test suite has two parts:

- dataset tests check that every spectrum parses with a valid header (DOI, solvent, units, file naming) and that every
  structure is a well-formed xyz file
- library tests check the spectroscopic code against analytic limits and sum rules (e.g.
  :math:`\int\varepsilon\,d\tilde\nu \propto f`, :math:`\Delta\varepsilon/\varepsilon = 4R/D`, recovery of known
  energy shifts).

The dataset tests loop over all files in ``data/``, so new data can be added by dropping ``.csv`` and ``.xyz`` files
into the existing folder structure; the CI pipeline then validates it automatically, so contributions from theorists
and experimentalists alike need no changes to the code.

With the environment from any option in :doc:`installation`:

.. code-block:: bash

   pytest tests -v                      # everything
   pytest tests -v -m dataset           # dataset validation only
   pytest tests -v -m "not dataset"     # library tests only, no dataset needed

Dataset paths are resolved relative to the repository, so ``pytest`` can be run
from any directory.
