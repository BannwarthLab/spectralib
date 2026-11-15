<p align="center">
  <img src="imgs/spectralib_logo.svg" alt="spectralib" width="320">
</p>

<h1 align="center">A Dataset for Luminescence and Circularly Polarized Luminescence Spectra</h1>

<p align="center">
  <a href="https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/pipelines"><img src="https://img.shields.io/gitlab/pipeline-status/rwth-bannwarthlab%2Fspectralib?gitlab_url=https://gitlab.git.nrw&branch=main" alt="Pipeline"></a>
  <img src="https://rwth-bannwarthlab.pages.git.nrw/spectralib/coverage.svg" alt="Coverage">
  <a href="https://rwth-bannwarthlab.pages.git.nrw/spectralib"><img src="https://img.shields.io/badge/docs-pages-blue" alt="Documentation"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue" alt="Python versions">
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-BSD--3--Clause-blue" alt="Code license: BSD-3-Clause"></a>
  <a href="data/LICENSE"><img src="https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey" alt="Data license: CC BY 4.0"></a>
</p>

---

This project contains experimental luminescence (LUM) and circularly polarized luminescence (CPL) spectra from published articles, together with Cartesian coordinates of the molecular structures (`xyz`) and molecular fingerprints ([MolBar](https://doi.org/10.1039/D4DD00208C), [InChI](https://www.inchi-trust.org/)). 
`spectralib` aims to provide a common ground for theoreticians and experimentalists alike.

## 🎯 Aims

- **Central storage** of experimental LUM and CPL spectroscopic data.
- **Standardized data:** `csv` files with one header line containing experimental conditions and DOI allowing comparison with other measurements or calculations.
- **Easy extension:** Data is checked with the CI/CD pipeline to identify formal errors reducing manual effort for contributors and maintainers, and keeping the dataset clean.
- **Analysis tools:** the `spectralib` Python package can be used to process spectroscopic data (reading, converting, comparing, plotting).

---

## 📦 Data

| Content | Location |
|---|---|
|  LUM and CPL spectra | `data/spectra/<id>/` |
|  Structures (`xyz` format, optimized with [GFN2-xTB](https://doi.org/10.1021/acs.jctc.8b01176)) with MolBar and InChI identifiers | `data/structures/<id>/` |
|  `spectralib` Python code | `src/spectralib/` |

---

## 🚀 Quick Start

Install [Miniforge](https://conda-forge.org/download/) (or use an existing Anaconda installation):

```bash
git clone https://gitlab.git.nrw/rwth-bannwarthlab/spectralib.git
cd spectralib
conda env create -f environment.yml
conda activate spectralib
pytest tests -m dataset # validate the dataset
```

```python
from spectralib import read_spectrum

spec = read_spectrum("data/spectra/9/9_CPL.csv")   # x in nm, y, and the header as spec.metadata
print(spec.metadata["molname"], spec.metadata["DOI"])
```

---

## 📚 Documentation

Please see the [documentation](https://rwth-bannwarthlab.pages.git.nrw/spectralib) for a more detailed overview:

| Topic | Content |
|---|---|
| [Overview of Existing Data](https://rwth-bannwarthlab.pages.git.nrw/spectralib/data.html) | Overview of all systems with references to the literature sources in the current version |
| [File Description](https://rwth-bannwarthlab.pages.git.nrw/spectralib/dataset.html) | Declaration of the file format for spectroscopic data, name convention, and more |
| [Tests for Data Consistency](https://rwth-bannwarthlab.pages.git.nrw/spectralib/testing.html) | Notes on tests done to ensure data consistency |
| [spectralib Python Library](https://rwth-bannwarthlab.pages.git.nrw/spectralib/usage.html) | Install instructions and usage examples of the Python library |

---

## Contributing

New data from **you** to this repository is welcome! Just add your files to `data/`, check them with `summarize_spectra data/spectra/<id>` and open a merge request, or simply open an [issue](https://gitlab.git.nrw/rwth-bannwarthlab/spectralib/-/issues) with the files attached. See the [contribution guide](https://rwth-bannwarthlab.pages.git.nrw/spectralib/contributing.html) for more details.

---

## 📝 How to Cite

Please cite the corresponding publication (M. Pauls, N. Maser, G. Feldmann, C. Bannwarth, *manuscript in preparation*) and state the dataset version you used. Citation metadata are provided in [`CITATION.cff`](CITATION.cff).

---

## 👥 Authors

- [Mike Pauls](mailto:pauls@pc.rwth-aachen.de)
- Nicole Maser
- Gereon Feldmann
- Christoph Bannwarth

---

## Acknowledgments

- The structures were optimized with [xtb](https://github.com/grimme-lab/xtb) (version 6.7.0, GFN2-xTB level of theory).
- The identifiers were computed with [MolBar](https://gitlab.git.nrw/rwth-bannwarthlab/molbar) (version 1.2.0) and [Open Babel](https://openbabel.org) (version 3.2.1).
- `spectralib` builds on NumPy, SciPy and Matplotlib. 

The references are listed in the [documentation](https://rwth-bannwarthlab.pages.git.nrw/spectralib/acknowledgments.html).

Parts of the code and documentation were drafted or revised with the help of generative AI (Claude, Anthropic) and reviewed by the authors. The initial code base, research ideas, scientific content and the curation of all data are the authors' own work, and the authors take full responsibility for the content of this repository.

---

## Funding
Funded by the Ministry of Culture and Science of the State of North Rhine-Westphalia (MKW) through the NRW Rückkehrprogramm and the Federal Ministry of Education and Research (BMBF) and the MKW under the Excellence Strategy of the Federal Government and the Länder.

---

## License

The code is licensed under [BSD-3-Clause](LICENSE), the data in `data/` under [CC BY 4.0](data/LICENSE).
