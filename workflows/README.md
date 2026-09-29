# Workflows (not part of the `cpl50` package)

Scripts moved here unchanged from `origin/mol_1-30` (N. Maser, commits `f70cc5f`, `ab7a1bc`)
so they no longer live inside `src/cpl50`, which is reserved for the importable library.
They are kept for discussion; nothing in `cpl50` imports them.

| Folder | Content |
|---|---|
| `dscfrunner/` | Multilevel excited-state workflow: TDDFT single point → if the dominant configuration weight of S<sub>n</sub> ≥ threshold, ΔSCF (UKS, `alphaconf`) opt+freq, otherwise / on failure TDDFT opt+freq. ORCA templates, SLURM submit script, `prep.sh` batch driver. |
| `md_spectra/` | Collect ORCA TDDFT output from MD snapshots (`0000/ … 0100/`), average stick spectra, broaden, plot against experiment. |

## Open points for discussion (found while moving, not changed)

### `dscfrunner/`
1. **`alphaconf` construction** (`build_alphaconf`): for HOMO→LUMO it yields `0,1` (fine). For a hole below the HOMO it writes `hole_offset+1` zeros followed by `virt-homo` ones, e.g. HOMO-1→LUMO+1 gives `0,0,1,1`, which (read as consecutive occupations) moves two electrons. Needs checking against ORCA's `alphaconf`/`ionizealpha` semantics before using it for non-HOMO→LUMO states.
2. **Open-shell singlet via UKS ΔSCF** gives a spin-mixed determinant (E<sub>mixed</sub> ≈ (E<sub>S</sub>+E<sub>T</sub>)/2). Spin purification (E<sub>S</sub> ≈ 2E<sub>mixed</sub> − E<sub>T</sub>) or ROKS should be decided on before it enters a benchmark.
3. `--tdfallback` is `action="store_true", default=True` → cannot be switched off from the CLI.
4. ORCA binary path is hard-coded in `run_orca`; `sys` reaches `dscfrunner_main.py` only through `from dscfrunner_functions import *`.
5. `prep.sh` keeps solvents and multiplicities as positional bash arrays indexed 0–25, while the templates always use charge `0`. The dataset already holds this information (`solv` in the csv headers, `.CHRG`/`.UHF` in `data/structures/<id>/`); `cpl50.io.read_charge_uhf` and `cpl50.io.read_spectrum(...).metadata["solv"]` can replace the arrays.

### `md_spectra/`
6. Depends on `src.utilities.convolution.compute_spectrum` from a private repo (`sys.path.append('/home/nmaser/...')`) and absolute paths to the dataset.
7. CPL sticks are normalised by the number of parsed snapshots, fluorescence sticks by `end-start+1` (number of folders requested) – inconsistent if a snapshot is missing.
8. For fluorescence *all* TDDFT roots of every snapshot are collected; for Kasha emission only the S<sub>1</sub>→S<sub>0</sub> transition should enter (as done for CPL).
9. eV↔nm conversion uses the rounded 1239.8 constant.

The library now covers the numerical parts of `md_spectra/`:
`cpl50.io_orca.read_orca_tddft`, `cpl50.broadening.ensemble_sticks`, `cpl50.broadening.broaden`/`emission_spectrum`,
`cpl50.broadening.fwhm_from_fw1e` (their width convention "full width at 1/e").
