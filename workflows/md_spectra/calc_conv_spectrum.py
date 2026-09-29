""""Script to perform a convolution of an MD averaged stick spectrum from orca TDDFT calculations. Output file: cpl_conv.txt and fluor_conv.txt"""

# Note: This script lies in the folder "spectra" inside the folder "tddft"


import numpy as np
import os
import re
import matplotlib.pyplot as plt 
import sys
sys.path.append('/home/nmaser/tddft_cpl/src')
from src.utilities.convolution import compute_spectrum
import argparse

parser = argparse.ArgumentParser(
        description="Calculate convolved spectrum for a given molecule"
        )
parser.add_argument(
        "mol",
        type=int,
        help="Molecule number from global benchmark"
        )
args = parser.parse_args()
mol_num = args.mol
print(f"Running spectrum calculation for molecule {mol_num}")


# function to read out the stick spectrum file 

def read_stick_spectrum(filename):
    """
    Parses an ECD stick spectrum text file and extracts:
    e_nm, e_ev, and val_vel, val_len as lists of floats.

    Returns:
        e_nm (list of float)
        e_ev (list of float)
        val_vel    (list of float)
        val_len    (list of float)
    """
    e_nm = []
    e_ev = []
    val_vel = []
    val_len = []

    with open(filename, "r") as f:
        lines = f.readlines()

    # Skip header (first line)
    for line in lines[1:]:
        if not line.strip():
            continue  # skip empty lines

        parts = line.split()
        if len(parts) < 4:
            continue

        try:
            e_nm.append(float(parts[0]))
            e_ev.append(float(parts[1]))
            val_vel.append(float(parts[2]))
            val_len.append(float(parts[3]))
        except ValueError:
            continue

    return e_nm, e_ev, val_vel, val_len


def perform_convolution(stick_e_ev, stick_value, start_conv, end_conv, FW_inv_e_M_ev=0.5):
    # all values in ev

    FWHM_ev = FW_inv_e_M_ev * np.sqrt(np.log(2))
    value_matrix = np.column_stack((np.array(stick_e_ev), np.array(stick_value))) 
    value_conv_data = compute_spectrum(value_matrix, espan = (start_conv,end_conv), width = FWHM_ev, step = 0.001)
    e_ev_conv = value_conv_data[:,0]
    e_nm_conv = [1239.8/i for i in e_ev_conv]
    value_conv = value_conv_data[:,1]

    return e_ev_conv, e_nm_conv, value_conv


### function to read out the exp spectrum

def read_csv(filename):
    """
    Reads a CSV file.
    First data column: energy
    Second data column: R
    """
    energy = []
    R = []

    with open(filename, "r") as f:
        lines = f.readlines()

    # skip metadata header (first line)
    for line in lines[1:]:
        line = line.strip()

        if not line:
            continue

        parts = line.split(",")

        if len(parts) < 2:
            continue

        try:
            energy.append(float(parts[0]))
            R.append(float(parts[1]))
        except ValueError:
            continue

    return energy, R


################ CPF ###########################

# read out cpf stick spectrum file
e_nm_cpf, e_ev_cpf, r_vel_cpf, r_len_cpf = read_stick_spectrum("cpl_stick.txt")

# perform convolution
start_conv_ev_cpf = 0.5
end_conv_ev_cpf = 5.0
FW_inv_e_M_ev_cpf = 0.5

e_ev_conv_cpf, e_nm_conv_cpf, r_len_conv_cpf = perform_convolution(e_ev_cpf, r_len_cpf, start_conv_ev_cpf, end_conv_ev_cpf, FW_inv_e_M_ev_cpf) # length
e_ev_conv_cpf, e_nm_conv_cpf, r_vel_conv_cpf = perform_convolution(e_ev_cpf, r_vel_cpf, start_conv_ev_cpf, end_conv_ev_cpf, FW_inv_e_M_ev_cpf) # velocity

# write output with convoluted spectrum  

with open("cpl_conv.txt", "w") as f:
    f.write('E (nm)   E (eV)      f velocity    f length (au**2)\n')
    for x, y, z, r in zip(e_nm_conv_cpf, e_ev_conv_cpf, r_vel_conv_cpf, r_len_conv_cpf):
        f.write(f"{x:.1f}\t{y:.6f}\t{z:.10f}\t{r:.10f}\n")
        #print(x)



################ FLUOR ###########################

# read out cpf stick spectrum file
e_nm_fluor, e_ev_fluor, r_vel_fluor, r_len_fluor = read_stick_spectrum("fluor_stick.txt")

# perform convolution
start_conv_ev_fluor = 0.5
end_conv_ev_fluor = 5.0
FW_inv_e_M_ev_fluor = 0.5

e_ev_conv_fluor, e_nm_conv_fluor, r_len_conv_fluor = perform_convolution(e_ev_fluor, r_len_fluor, start_conv_ev_fluor, end_conv_ev_fluor, FW_inv_e_M_ev_fluor) # length
e_ev_conv_fluor, e_nm_conv_fluor, r_vel_conv_fluor = perform_convolution(e_ev_fluor, r_vel_fluor, start_conv_ev_fluor, end_conv_ev_fluor, FW_inv_e_M_ev_fluor) # velocity

# write output with convoluted spectrum  

with open("fluor_conv.txt", "w") as f:
    f.write('E (nm)   E (eV)      f velocity    f length (au**2)\n')
    for x, y, z, r in zip(e_nm_conv_fluor, e_ev_conv_fluor, r_vel_conv_fluor, r_len_conv_fluor):
        f.write(f"{x:.1f}\t{y:.6f}\t{z:.10f}\t{r:.10f}\n")
        #print(x)





###### TEST ###############

# plot the spectra next to the exp spectrum
cpl_path = f"/home/nmaser/benchmark/cpl50/data/spectra/{mol_num}/{mol_num}_CPL.csv"
e_nm_cpf_exp, r_cpf_exp = read_csv(cpl_path)


#### norm the maxima to 1
r_vel_cpf_abs = [abs(i) for i in r_vel_cpf]
r_len_cpf_abs = [abs(i) for i in r_len_cpf]
r_vel_conv_cpf_abs = [abs(i) for i in r_vel_conv_cpf]
r_len_conv_cpf_abs = [abs(i) for i in r_len_conv_cpf]
r_cpf_exp_abs = [abs(i) for i in r_cpf_exp]

r_vel_cpf_normed = [i/max(r_vel_cpf_abs) for i in r_vel_cpf]
r_len_cpf_normed = [i/max(r_len_cpf_abs) for i in r_len_cpf]
r_vel_conv_cpf_normed = [i/max(r_vel_conv_cpf_abs) for i in r_vel_conv_cpf]
r_len_conv_cpf_normed = [i/max(r_len_conv_cpf_abs) for i in r_len_conv_cpf]
r_cpf_exp_normed = [i/max(r_cpf_exp_abs) for i in r_cpf_exp]


plt.figure()
plt.title(f"CPF (FW at 1/e = {FW_inv_e_M_ev_cpf} eV), molecule {mol_num}")
#plt.stem(e_nm_cpf, r_vel_cpf, markerfmt='none',  basefmt='gray', linefmt='gray', label='R (velocity)') # vel red
plt.plot(e_nm_conv_cpf, r_vel_conv_cpf_normed, color = 'red', label='R (velocity)')
plt.plot(e_nm_conv_cpf, r_len_conv_cpf_normed, color = 'blue', label='R (length)')
plt.plot(e_nm_cpf_exp, r_cpf_exp_normed, color = 'green', label='Experiment')
plt.xlabel("excitation energies / nm")
plt.ylabel("R (norm.)")
plt.legend()
plt.savefig("cpf.png",dpi=300,bbox_inches='tight')


### read out fluor + plot

fluor_path = f"/home/nmaser/benchmark/cpl50/data/spectra/{mol_num}/{mol_num}_LUM.csv"
e_nm_fluor_exp, r_fluor_exp = read_csv(fluor_path)

#### norm the maxima to 1
r_vel_fluor_normed = [i/max(r_vel_fluor) for i in r_vel_fluor]
r_vel_conv_fluor_normed = [i/max(r_vel_conv_fluor) for i in r_vel_conv_fluor]
r_len_conv_fluor_normed = [i/max(r_len_conv_fluor) for i in r_len_conv_fluor]
r_fluor_exp_normed = [i/max(r_fluor_exp) for i in r_fluor_exp]


plt.figure()
plt.title(f"Fluorescence (FW at 1/e = {FW_inv_e_M_ev_fluor} eV), molecule {mol_num}")
#plt.stem(e_nm_fluor, r_vel_fluor, markerfmt='none',  basefmt='gray', linefmt='gray', label='R (velocity)') # vel red
plt.plot(e_nm_conv_fluor, r_vel_conv_fluor_normed, color = 'red', label='R (velocity)')
plt.plot(e_nm_conv_fluor, r_len_conv_fluor_normed, color = 'blue', label='R (length)')
plt.plot(e_nm_fluor_exp, r_fluor_exp_normed, color = 'green', label='Experiment')
plt.xlabel("excitation energies / nm")
plt.ylabel("R (norm.)")
plt.legend()
plt.savefig("fluor.png",dpi=300,bbox_inches='tight')


