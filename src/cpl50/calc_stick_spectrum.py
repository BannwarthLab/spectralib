""""Script to calculate an MD averaged stick spectrum from orca TDDFT calculations. Output file: cpl_stick.txt and fluor_stick.txt"""

# Note: This script lies in the folder "spectra" inside the folder "tddft"


import numpy as np
import os
import re
import matplotlib.pyplot as plt 
import sys
sys.path.append('/home/nmaser/tddft_cpl/src')
from src.utilities.convolution import compute_spectrum



##### functions to parse data for md averaged cpl spectra

def parse_orca_cd_first_transition(orca_out_path):
    """
    Extract the first CD transition from both electric-
    and velocity-dipole tables.
    """

    with open(orca_out_path) as f:
        lines = f.readlines()

    e_ev = e_nm = R_length = R_velocity = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Electric dipole table ---
        if "CD SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
            i += 1
            # skip header lines until we reach data
            while i < len(lines) and not re.match(r"\s*\d+-\d+A", lines[i]):
                i += 1

            fields = lines[i].split()
            e_ev = float(fields[3])
            e_nm = float(fields[5])
            R_length = float(fields[6])

        # --- Velocity dipole table ---
        if "CD SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS" in line:
            i += 1
            while i < len(lines) and not re.match(r"\s*\d+-\d+A", lines[i]):
                i += 1

            fields = lines[i].split()
            R_velocity = float(fields[6])

        i += 1

    if None in (e_ev, e_nm, R_length, R_velocity):
        raise ValueError(f"Incomplete CD data in {orca_out_path}")

    return e_ev, e_nm, R_length, R_velocity



def collect_cd_data(base_dir=".", start=0, end=80):
    """
    Collect CD data from folders base_dir/0000 ... base_dir/0080

    Returns
    -------
    data : list of tuples
        (e_ev, e_nm, R_length, R_velocity, folder)
    """

    data = []

    for i in range(start, end + 1):
        folder = f"{i:04d}"
        out_file = os.path.join(base_dir, folder, "orca.out")

        if not os.path.isfile(out_file):
            continue

        try:
            e_ev, e_nm, R_length, R_velocity = parse_orca_cd_first_transition(out_file)
            data.append((e_ev, e_nm, R_length, R_velocity, folder))
        except ValueError as err:
            print(err)

    return data


def sort_cd_data(data, descending=True):
    """
    Sort CD data by e_ev.

    Parameters
    ----------
    data : list of tuples
    descending : bool

    Returns
    -------
    sorted_data : list of tuples
    """

    return sorted(data, key=lambda x: x[0], reverse=descending)

def normalize_R_values(data):
    """
    Divide R_length and R_velocity by the number of entries.

    Parameters
    ----------
    data : list of tuples
        (e_ev, e_nm, R_length, R_velocity, folder)

    Returns
    -------
    normalized_data : list of tuples
        same structure as input
    """

    N = len(data)
    if N == 0:
        raise ValueError("No data to normalize")

    normalized = []
    for e_ev, e_nm, R_len, R_vel, folder in data:
        normalized.append(
            (e_ev, e_nm, R_len / N, R_vel / N, folder)
        )

    return normalized


data = collect_cd_data(base_dir="..", start=0, end=100)
# Normalize R values
data = normalize_R_values(data)
# Sort by energy (descending)
data_sorted = sort_cd_data(data, descending=True)

# Split into lists
e_ev = [d[0] for d in data_sorted]
e_nm = [d[1] for d in data_sorted]
R_length = [d[2] for d in data_sorted]
R_velocity = [d[3] for d in data_sorted]
folders = [d[4] for d in data_sorted]


#############################################################
###### write output for cpl spectra

with open("cpl_stick.txt", "w") as f:
    f.write('E (nm)   E (eV)      R velocity    R length (10^40 cgs)\n')
    for x, y, z, r in zip(e_nm, e_ev, R_velocity, R_length):
        f.write(f"{x:.1f}\t{y:.6f}\t{z:.10f}\t{r:.10f}\n")
        #print(x)



#############################################################






##### functions to parse data for md averaged fluor spectra


def read_all_abs_transitions(filename="orca.out"):
    """
    Reads an ORCA output file and returns all transition energies
    and oscillator strengths from the absorption spectrum sections.
    """
    e_cm = []
    e_nm = []
    f_len_values = []
    f_vel_values = []

    with open(filename, "r") as f:
        lines = f.readlines()

    # ---------- electric dipole (length) ----------
    in_f_len_section = False

    for line in lines:
        if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
            in_f_len_section = True
            continue

        if in_f_len_section:
            stripped = line.strip()

            if stripped.startswith("-"):
                continue

            if not stripped:
                break

            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    e_cm.append(float(parts[4]))
                    e_nm.append(float(parts[5]))
                    f_len_values.append(float(parts[6]))
                except ValueError:
                    continue

    # ---------- velocity dipole ----------
    in_f_vel_section = False

    for line in lines:
        if "ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS" in line:
            in_f_vel_section = True
            continue

        if in_f_vel_section:
            stripped = line.strip()

            if stripped.startswith("-"):
                continue

            if not stripped:
                break

            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    # fosc(P2) column
                    f_vel_values.append(float(parts[6]))
                except ValueError:
                    continue

    if not e_cm:
        print(f"No transitions found in {filename}")

    return e_cm, e_nm, f_len_values, f_vel_values


def collect_all_abs_data_normalized_sorted(base_path=".", start=0, end=100):
    """
    Collects all abs transitions from folders 0000–0100,
    normalizes f by total number of folders,
    and returns wavelength-sorted lists.
    """
    e_cm_all = []
    e_nm_all = []
    f_len_all = []
    f_vel_all = []

    total_folders = end - start + 1

    for i in range(start, end + 1):
        folder = f"{i:04d}"
        orca_file = os.path.join(base_path, folder, "orca.out")

        if not os.path.isfile(orca_file):
            continue

        try:
            e_cm, e_nm, f_len, f_vel = read_all_abs_transitions(orca_file)
            e_cm_all.extend(e_cm)
            e_nm_all.extend(e_nm)
            f_len_all.extend(f_len)
            f_vel_all.extend(f_vel)

        except ValueError:
            continue

    # Normalize R
    f_len_all = [r / total_folders for r in f_len_all]
    f_vel_all = [r / total_folders for r in f_vel_all]

    # 🔹 Sort by energy (cm⁻¹), descending
    # zip *all* arrays together
    sorted_pairs = sorted(
        zip(e_cm_all, e_nm_all, f_len_all, f_vel_all),
        key=lambda x: x[0],      # sort by e_cm
        reverse=True
    )
    # unzip back into separate lists
    e_cm_sorted, e_nm_sorted, f_len_sorted, f_vel_sorted = map(list, zip(*sorted_pairs))


    return e_cm_sorted, e_nm_sorted, f_len_sorted, f_vel_sorted






#############################################################
###### write output for fluorescence spectra

### read all out 
e_cm_fl, e_nm_fl, f_len_fl, f_vel_fl = collect_all_abs_data_normalized_sorted(base_path="..", start=0, end=100)

# convert nm to ev 
e_ev_fl = [1239.8/i for i in e_nm_fl]



# write outputs into spectrum folder


with open("fluor_stick.txt", "w") as f:
    f.write('E (nm)   E (eV)      f velocity    f length (au**2)\n')
    for x, y, z, r in zip(e_nm_fl, e_ev_fl, f_vel_fl, f_len_fl):
        f.write(f"{x:.1f}\t{y:.6f}\t{z:.10f}\t{r:.10f}\n")
        #print(x)


         


#############################################################
