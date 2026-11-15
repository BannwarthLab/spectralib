# Data

| Path | Content |
|---|---|
| `spectra/<id>/<id>_LUM.csv` | luminescence spectrum |
| `spectra/<id>/<id>_CPL.csv` | CPL spectrum |
| `spectra/<id>/<id>_LUM_<int>.csv` | further measurement of the same system under other conditions (e.g. temperature) |
| `structures/<id>/<id>.xyz` | GFN2-xTB structure (xtb 6.7.0), coordinates in Å |
| `structures/<id>/<id>.molbar`, `<id>.inchi` | MolBar and InChI of the structure |
| `structures/<id>/.CHRG`, `.UHF` | charge and unpaired electrons, only if not 0 |

Systems with several molecules carry letters, e.g. `41a`, `41b`, and `41ab` for their complex.

Each spectrum starts with one header line, followed by `<wavelength in nm>,<value>` per line:

```text
DOI,molname,T,c,solv,irrad,quant,unit
10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0
```

`T` in K, `c` in mol/L, `irrad` in nm; `0` means not reported. The fields, the accepted solvents and the
article of every system are described in the
[documentation](https://rwth-bannwarthlab.pages.git.nrw/spectralib/dataset.html).

Check files with `summarize_spectra data/spectra/<id>` or `pytest tests -m dataset`.
The data are licensed under [CC BY 4.0](LICENSE).
