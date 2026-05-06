# A Dataset for Luminescence and Circularly Polarized Luminescence Data

[![License](https://img.shields.io/badge/License-CC%20BY%20SA%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![Repository](https://img.shields.io/badge/Repository-RWTH%20Aachen-blue)](https://git.rwth-aachen.de/bannwarthlab/cpl50)

![Lewis Structures](./structures.pdf)

This project collects: 
- Experimental luminescence (`data/spectra/*LUM.csv`) and CPL (`data/spectra/*CPL.csv`) spectra
- Molecular Structures (`data/structures/*.xyz`) in xyz format.


# File Description
Each `.csv` file contains a 1-line header with information about the experiments in the format:

`DOI,molname,T,c,solv,irrad,quant,unit`

with:
- `DOI`: The doi to the article the data was extracted from.

- `molname`: A short description/alias of the respective molecule, typically one that is given in the corresponding article.

- `T`: The temperature (in K) at which the measurements were performed. 
    If none was given/found, `0` is added here. "Room temperature" is always set to 293.15 K.

- `c`: The concentration (in M) at which the measurements were performed.
    If none was given/found, `0` is added here.
- `solv`: A (short) name of the solvent used in the experiments.
    A list of supported solvents for the tests may be found in `src/cpl50/utils.py`.

- `irrad`: The used irradiation wavelength (in nm).
    If none was given/found, `0` is added here.

- `quant`: The experimental quantity measured, e.g. $\Delta I$ (`di`) in CPF.

- `unit`: The unit of `quant`, if provided. 
    If none was given/found, or the quantity is dimensionless, `0` is added here.


A valid example header, e.g., for molecule 60 (`data/spectra/60/60_CPL.csv`) looks like this: 

`10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0`

This refers to the CPL spectrum of FL1-C1 from [this article](10.3390/molecules23102606), measured at room temperature (293.15 K) with a concentration of 5e-5 M in MeOH using $\lambda_\mathrm{irr} = 255~\mathrm{nm}$. The reported intensity is a $\Delta I$.

### Further Notes: 
- Measurements in thin films or matrices are omitted and deliberately excluded from the dataset at the moment.
- Some geometries were simplified (truncation of flexible alkane chains, tBu -> Me, etc.) to be computationally more tractable, and may differ from the Lewis structures illustrated above.  

### Data Format

- CPL spectra: 
```bash
<header>
<wavelength1>, <quant1>
<wavelength2>, <quant2>
...
```
- Molecular Geometries (in xyz format): 
```bash
<natoms>
<comment line>
<element1> <x1> <y1> <z1>
<element2> <x2> <y2> <z2>
...
```
All geometries are optimized with the [semiempirical electronic structure theory method GFN2-xTB](https://pubs.acs.org/doi/10.1021/acs.jctc.8b01176) as implemented in the [xtb program](https://github.com/grimme-lab/xtb) (version 6.7.0):
`xtb coord.xyz --opt --chrg <int> --uhf <int>`
If molecules are charged or have unpaired electrons in their electronic ground states, this information is contained in the `.CHRG` and `.UHF` files. 

## Running Tests

Simply install the dependencies in a virtual environment, and run the tests with `pytest`:
```bash
python3 -m venv .venv 
source .venv/bin/activate
pip install -e ."[test]"
python3 -m pytest tests -v
```


# Overview of Existing Data

| Index | Reference |
|------|-------|
| 1 | [Mol 2](https://www.sciencedirect.com/science/article/pii/S1010603015004414) |
| 2,3 | [Extract mol c1, c3](https://pubs.acs.org/doi/full/10.1021/acs.jctc.6b00109), [Experimental ref](https://pubs.acs.org/doi/full/10.1021/jp4105695) |
| 4  | [Sila-Helicene 3 (Fig. 1)](https://pubs.acs.org/doi/10.1021/ol4005036) |
| 5 | [Pt Helicene 3a](https://pubs.rsc.org/en/content/articlepdf/2014/sc/c3sc53442a) |
| 6–8 | [Switchable Bishelicene Zn](https://pubs.acs.org/doi/full/10.1021/acs.joc.9b00389), [Correction](https://pubs.acs.org/doi/10.1021/acs.joc.9b01513) |
| 9,10  | [(S)-1 and -2](https://doi.org/10.1002/asia.201200725) |
| 11 | [Nur 1](https://pubs.acs.org/doi/full/10.1021/acs.joc.7b00511) |
| 12 | [$\Delta_\mathrm{Ir}-\mathbf{A}$](https://onlinelibrary.wiley.com/doi/epdf/10.1002/anie.201704263) |
| 13 | [system 2](https://pubs.acs.org/doi/full/10.1021/acs.jpcc.7b00654) |
| 14 | [system 3](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/cptc.201700106) |
| 15 | [system 1](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/chem.201602684) |
| 16,17 | [System 1 und 5](https://onlinelibrary.wiley.com/doi/epdf/10.1002/chir.22176) |
| 18 | [Iridium Complex](https://www.sciencedirect.com/science/article/pii/S0021967316306501) |
| 19,20 | [Fig. S6 in SI](https://pubs.acs.org/doi/full/10.1021/ja300278e) |
| 21 | [mol 1, Fig. 3](https://pubs.rsc.org/en/content/articlehtml/2016/sc/c6sc01808d) |
| 22 | [mol 10](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201801908) |
| 23 | [schema 1](https://pubs.acs.org/doi/full/10.1021/jp504307v) |
| 24 | [mol 8b](https://pubs.acs.org/doi/full/10.1021/jacs.7b06848) |
| 25 | [CPF TADF mol](https://pubs.rsc.org/en/content/articlepdf/2015/cc/c5cc04105h) |
| 26 | [CPL TADF mol 1](https://pubs.acs.org/doi/full/10.1021/jacs.6b00850) |
| 27 | [CPL TADF mol 1, BODIPY](https://pubs.acs.org/doi/full/10.1021/ja412294s) |
| 28 | [Chiral TTM Radical](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.202000098) |
| 29 | [TTMCz kuehne](https://chemrxiv.org/doi/full/10.26434/chemrxiv.10001626/v1) |
| 30 | [radical anion NDI](https://pubs.acs.org/doi/full/10.1021/acs.jpclett.9b02269) |
| 31 | Data needs to be scaled by 1e-4 [TADF mol](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/adfm.201800051) |
| 32 | Scale cpl 1e-3 [Cyclophane](https://pubs.acs.org/doi/full/10.1021/acs.orglett.8b02995) |
| 33 | [molecular assembly cpf](https://pubs.acs.org/doi/full/10.1021/acs.jpclett.1c02013) |
| 34 | [3PhC](https://pubs.rsc.org/en/content/articlelanding/2015/tc/c4tc02339k) |
| 35 | No Lum given! [Fig. 4 spec](https://www.pnas.org/doi/epdf/10.1073/pnas.1717524114) |
| 36 | [(R)-1](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201702143) |
| 37 | (R,R,R)-2 |
| 38 | [mol 1](https://pubs.acs.org/doi/full/10.1021/acs.orglett.7b02337) |
| 39 | [(+)-(12,4)BBBB-[4]CAn2,6](https://onlinelibrary.wiley.com/doi/full/10.1002/ange.201909401)|
| 42 | [Mol C3](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/chem.201402930) |
| 43 | [mol 5](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/ejoc.201501181) |
| 44 | [mol 9](https://pubs.acs.org/doi/full/10.1021/jacs.7b05671) scale 1e-3 |
| 45 | [mol 1 protonated](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201603591) |
| 46 | [mol 1c](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201604398) |
| 47 | [mol 1c](https://pubs.acs.org/doi/full/10.1021/acs.joc.7b01087) |
| 48 | [mol 1](https://pubs.acs.org/doi/10.1021/acs.orglett.6b00747) |
| 50 | [mol 7aa](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201605000) |
| 51 | [mol 1](https://pubs.rsc.org/en/content/articlelanding/2015/ra/c4ra11488d) |
| 52 | mol 2 |
| 53 | mol 3 |
| 54 | [mol 1](https://www.mdpi.com/1420-3049/23/10/2606) scale w 1e-3 |
| 55 | mol 2, scale w 1e-3 | 
| 56 |mol 3, scale with 1e-3 | 
| 57 | mol 4, scale with 1e-3 | 
| 58 | Ph3, scale with 1e-3
| 59 | 12-CPP, scale with 1e-3 |
| 60 | FL1-C1, scale with 1e-3 |

# Quicknotes
- Add tests that check validity of headers provided
    - within header: zeros are fine, doi has to be present all the time
- add a function to write out information about the set, eg. a formatted information header per structure
- Add analysis folder for overlap calculation etc.
- Add tests that check that all spectra can be parsed




---
**NOTE** 
> Please see Tab. XX in the corresponding publication (G. Feldmann, N. Maser, M. Pauls, C. Bannwarth, *manuscript in preparation*) for additional references.  
---

## Contributions

*Add description on how to add data*

## Contact

Mike Pauls, pauls@pc.rwth-aachen.de
