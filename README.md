# CPL50: A Benchmark Set for Circularly Polarized Luminescence

[![License](https://img.shields.io/badge/License-CC%20BY%20SA%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![Repository](https://img.shields.io/badge/Repository-RWTH%20Aachen-blue)](https://git.rwth-aachen.de/bannwarthlab/cpl50)


This project collects: 
- Experimental CPL (`data/spectra/*CPL.csv`) and luminescence spectra (`data/spectra/*LUM.csv`)
- Molecular Structures (`data/structures/*.xyz`) 

## Running Tests

Install optional test dependencies:

```bash
python -m pip install -e .[test]
```

Run the suite from the repository root:

```bash
python -m pytest tests -v
```

## File Description
Each spectrum .csv file contains a 1-line header with information about the experiments in the following format:

`DOI,molname,T,c,solv,irrad,quant,unit`

with:
- `DOI`: The doi to the article the data was extracted from
- `molname`: A short description/alias of the respective molecule that is typically given in the corresponding article
- `T`: The temperature (in K) at which the measurements were performed.
- `c`: The concentration (in M) at which the measurements were performed.
- `solv`: A short name for the solvent used in the experiment.
- `irrad`: The used irradiation wavelength (in nm).
- `quant`: The experimental quantity measured, e.g. $\Delta I$ in CPF.
- `unit`: The unit of `quant`, if provided. 

A valid example header, e.g., for 60 (`data/spectra/60/60_CPL.csv`) looks like this: 

`10.3390/molecules23102606,FL1-C1,293.15,5e-5,meoh,255,di,0`

This refers to the CPL spectrum of FL1-C1 from [article](10.3390/molecules23102606) measured at room temperature (293.15 K) with a concentration of 5e-5 M in MeOH using $\lambda_\mathrm{irr} = 255~\mathrm{nm}$. 
The reported intensity is a dimensionless $\Delta I$.

Further Notes: 
- If information of a header entry is missing, it is replaced with `0`
- "Room temperature" is always set to 293.15 K per default.
- Measurements in thin films or matrices are omitted and deliberately excluded from the CPL50 set.

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

## Work in Progress
- <span style="color:red">Add GFN2-xTB (v.6.7.0) optimized geometries (xtbopt.xyz) as is with the mol. idx name (cf. example 61): 
`xtb coord.xyz --opt --chrg <int>`
</span>.

Ideal scenario would be sth like "measured at 298 K in DCM with c = 1e-5 M" so we give: `<DOI>,(R),298.00,1.0e-5,CH2Cl2,360` 

Notation for data "structure,CPF,LUM": "xxx/ooo"


| Index | Notes | Reference |
|------|-------|----------|
| 1 | A | [Extract mol 2 and spectra (large CPF signal)](https://www.sciencedirect.com/science/article/pii/S1010603015004414) |
| 2,3 | A | [Extract mol c1, c3](https://pubs.acs.org/doi/full/10.1021/acs.jctc.6b00109), [Experimental ref](https://pubs.acs.org/doi/full/10.1021/jp4105695) |
| 4 | A | [Sila-Helicene 3 (Fig. 1)](https://pubs.acs.org/doi/10.1021/ol4005036) |
| 5 | A | [Pt Helicene 3a](https://pubs.rsc.org/en/content/articlepdf/2014/sc/c3sc53442a) |
| 6–8 | A | [Switchable Bishelicene Zn](https://pubs.acs.org/doi/full/10.1021/acs.joc.9b00389), [Correction](https://pubs.acs.org/doi/10.1021/acs.joc.9b01513) |
| 9,10 | A | [(S)-1 and -2](https://doi.org/10.1002/asia.201200725) |
| 11 | A | [Nur 1](https://pubs.acs.org/doi/full/10.1021/acs.joc.7b00511) |
| 12 | A | [$\Delta_\mathrm{Ir}-\mathbf{A}$](https://onlinelibrary.wiley.com/doi/epdf/10.1002/anie.201704263) |
| 13 | A | [system 2](https://pubs.acs.org/doi/full/10.1021/acs.jpcc.7b00654) |
| 14 | A | [system 3](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/cptc.201700106) |
| 15 | A | [system 1](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/chem.201602684) |
| 16,17 | A | [System 1 und 5](https://onlinelibrary.wiley.com/doi/epdf/10.1002/chir.22176) |
| 18 | A | [Iridium Complex](https://www.sciencedirect.com/science/article/pii/S0021967316306501) |
| 19,20 | A | [Fig. S6 in SI](https://pubs.acs.org/doi/full/10.1021/ja300278e) |
| 21 | A | [mol 1, Fig. 3](https://pubs.rsc.org/en/content/articlehtml/2016/sc/c6sc01808d) |
| 22 | A | [mol 10](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201801908) |
| 23 | A | [schema 1](https://pubs.acs.org/doi/full/10.1021/jp504307v) |
| 24 | A | [mol 8b](https://pubs.acs.org/doi/full/10.1021/jacs.7b06848) |
| 25 | A | [CPF TADF mol](https://pubs.rsc.org/en/content/articlepdf/2015/cc/c5cc04105h) |
| 26 | A | [CPL TADF mol 1](https://pubs.acs.org/doi/full/10.1021/jacs.6b00850) |
| 27 | A | [CPL TADF mol 1, BODIPY](https://pubs.acs.org/doi/full/10.1021/ja412294s) |
| 28 | A | [Chiral TTM Radical](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.202000098) |
| 29 | A | [TTMCz kuehne](https://chemrxiv.org/doi/full/10.26434/chemrxiv.10001626/v1) |
| 30 | A | [radical anion NDI](https://pubs.acs.org/doi/full/10.1021/acs.jpclett.9b02269) |
| 31 | oxx | Data needs to be scaled by 1e-4 | [biphenyl](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/adfm.201800051) |
| 32 | A | [Cyclophane](https://pubs.acs.org/doi/full/10.1021/acs.orglett.8b02995) |
| 33 | A | [molecular assembly cpf](https://pubs.acs.org/doi/full/10.1021/acs.jpclett.1c02013) |
| 34 | A | [3PhC](https://pubs.rsc.org/en/content/articlelanding/2015/tc/c4tc02339k) |
| 35 | A | [Fig. 4 spec](https://www.pnas.org/doi/epdf/10.1073/pnas.1717524114) |
| 36,37 | A | [mol 1,2](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201702143) |
| 38 | A | [mol 1](https://pubs.acs.org/doi/full/10.1021/acs.orglett.7b02337) |
| 39 | A | [mol 30](https://pubs.rsc.org/en/content/articlehtml/2012/nm/d3cc04187e) |
| 40 | A | [Mol 1](https://pubs.rsc.org/en/content/articlehtml/2015/cc/c5cc03054d) |
| 41 | A | [mol 2](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201600891) |
| 42 | A | [Mol C3](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/chem.201402930) |
| 43 | A | [mol 5](https://chemistry-europe.onlinelibrary.wiley.com/doi/epdf/10.1002/ejoc.201501181) |
| 44 | A | [mol 9](https://pubs.acs.org/doi/full/10.1021/jacs.7b05671) |
| 45 | A | [mol 1 protonated](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201603591) |
| 46 | A | [mol 1c](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201604398) |
| 47 | A | [mol 1c](https://pubs.acs.org/doi/full/10.1021/acs.joc.7b01087) |
| 48 | A | [mol 1](https://pubs.acs.org/doi/10.1021/acs.orglett.6b00747) |
| 49 | A | [mol 4](https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/chem.201801414) |
| 50 | A | ox |
| 51–53 | A | [mol 1–3](https://pubs.rsc.org/en/content/articlelanding/2015/ra/c4ra11488d) |
| 52 |x  | get spectra 
| 53 | xxx | -|
| 54 | xxx | [naphtol bis pyrene](https://www.mdpi.com/1420-3049/23/10/2606) scale w 1e-3 |
| 55 | xxx | scale w 1e-3 | 
| 56 | xxx | scale with 1e-3 | 
| 57 | xxx | scale with 1e-3 | 
| 58 | xxx | scale with 1e-3
| 59 | xxx | Scale with 1e-3 |
| 60 | xxx | Data needs to be scaled by 1e-3 |

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
