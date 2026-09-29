"""Contains functions for the dscfrunner."""
from __future__ import annotations
import subprocess
import time
import os
import re
import sys


def run_orca(inp: str, out: str) -> None:
    """Run an ORCA calculation locally and write output to file.

    Args:
        inp (str): ORCA input file.
        out (str): ORCA output file.
    """
    log(f"Running ORCA: {inp} → {out}")

    with open(out, "w") as f:
        res = subprocess.run(
            ["/mnt/group-bin/orca_6_1_0_linux_x86-64_shared_openmpi418/orca", inp],
            stdout=f,
            stderr=subprocess.STDOUT,
        )

    if res.returncode != 0:
        log(f"ORCA execution failed for {inp}")
        sys.exit(1)


def terminated_successfully(outfile : str) -> None:
    """Function to check if the orca calculation terminated sucessfully.

    Args:
        outfile (str): Name of the desired orca output file that has to be checked.
    """
    with open(outfile) as f:
        return any("ORCA TERMINATED NORMALLY" in line for line in f)


def is_done(outfile : str) -> bool:
    """Function to check if the desired output file already exists.

    Args:
        outfile (str): Name of the desired orca output file.
        
    Returns:
        bool: True if the output file exists and the calculation
        terminated successfully. False otherwise.
    """
    return os.path.exists(outfile) and terminated_successfully(outfile)


#def parse_tddft_weights(outfile: str, 
#                        state: int = 1
#                        ) -> list[float]:
#    """Function to parse the weights of the configurations from the TDDFT SP clauclation.
#
#    Args:
#        outfile (str): Name of the orca outfile of the TDDFT SP calculation.
#        state (int): Excited state number to parse. Defaults to 1.
#
#    Returns:
#        list[float]: List of configuration weights for the specified state.
#    """
#    weights = []
#    grab = False
#
#    state_header = re.compile(rf"STATE\s+{state}:")
#
#    with open(outfile) as f:
#        for line in f:
#            # Start of desired state
#            if state_header.search(line):
#                grab = True
#                continue

            # Next state reached → stop
#            if grab and line.strip().startswith("STATE"):
#                break

#            if grab:
#                # Match lines like: "84a ->  86a  :     0.506581"
#                m = re.search(r":\s*([0-9]*\.[0-9]+)", line)
#                if m:
#                    weights.append(float(m.group(1)))

#    return weights


def parse_tddft_excitations(outfile: str, 
                            state: int = 1
                            ) -> list[tuple[int, int, float]]:
    """Function to parse the TDDFT excitations for a given state.

        Args:
        outfile (str): Name of the orca outfile of the TDDFT SP calculation.
        state (int): Excited state number to parse. Defaults to 1.

    Returns:
        list of (occ, virt, weight)
    """
    excitations = []
    grab = False
    state_header = re.compile(rf"STATE\s+{state}:")

    with open(outfile) as f:
        for line in f:
            if state_header.search(line):
                grab = True
                continue

            if grab and line.strip().startswith("STATE"):
                break

            if grab:
                m = re.search(r"(\d+)a\s*->\s*(\d+)a\s*:\s*([0-9]*\.[0-9]+)", line)
                if m:
                    occ = int(m.group(1))
                    virt = int(m.group(2))
                    weight = float(m.group(3))
                    excitations.append((occ, virt, weight))

    return excitations


def dominant_excitation(excitations: list[tuple[int, int, float]]
                        ) -> tuple[int, int, float]:
    """Function to return the dominant excitation (= maximum weight).

        Args:
        excitations list[tuple[int, int, float]: List of (occ, virt, weight) of all excitations of a state.

    Returns:
        tuple[int, int, float]: Tuple of (occ, virt, weight) of the dominant excitation of a state.
    """    
    return max(excitations, key=lambda x: x[2])



def get_homo_index(excitations: list[tuple[int, int, float]]
                                ) -> int:
    """Function to determine the index of the HOMO from the excitations of an ORCA output.

        Args:
        excitations (list[tuple[int, int, float]): List of (occ, virt, weight) of all excitations of a state.

    Returns:
        (int): Index of the HOMO, which is determined as the largest index among the occ indices.
    """   
    occ_indices = [occ for occ, _, _ in excitations]
    return max(occ_indices)


def build_alphaconf(occ: int, 
                    virt: int, 
                    homo: int
                    ) -> str:
    """Function to generate the alphaconf string from the dominant excitation.

        Args:
        occ (int): Index of the occupied MO involved in the dominant excitation.
        virt (int): Index of the virtual MO involved in the dominant excitation.
        homo (int): Index of the HOMO.

        Returns:
        (str): Occupation vector string that can be used for alphaconf in the DeltaSCF orca input file: '0' denotes a hole (removed electron); '1' denotes a particle (added electron).

    """   
    # offset of the hole relative to the HOMO
    hole_offset = homo - occ
    # how many orbitals above the HOMO does the excited electron go
    # = number of 1s in the string
    particle = virt - homo

    # check if the excitation is sensible:
    # - the excitation cannot occur from above the HOMO 
    if hole_offset < 0:
        raise ValueError("Occupied orbital lies above HOMO")
    # - the particle must go to a virtual orbital
    if particle < 1:
        raise ValueError("Virtual orbital must lie above HOMO")

    # how far below the HOMO does the hole lie = number of zeros before the first 1 
    zeros = hole_offset + 1  
    # number of ones in the string
    ones = particle

    # build the string: 0s from holes, then 1s from particles
    conf = ["0"] * zeros + ["1"] * ones
    return ",".join(conf)


# function to overwrite the alphaconf string in the dscf input
def update_alphaconf_in_input(
    infile: str,
    new_alphaconf: str
) -> None:
    """Function to overwrite the alphaconf line in the DeltaSCF ORCA input file.

    Args:
        infile (str): DeltaSCF ORCA input file to modify.
        new_alphaconf (str): New alphaconf vector, e.g. "0,1,1".
    """
    updated = False
    lines = []

    with open(infile) as f:
        for line in f:
            if "alphaconf" in line:
                lines.append(f"%scf alphaconf {new_alphaconf}\n")
                updated = True
            else:
                lines.append(line)

    if not updated:
        raise RuntimeError(f"No alphaconf line found in {infile}")

    with open(infile, "w") as f:
        f.writelines(lines)




def log(msg: str) -> None:
    """Save a message to the log file "dscfrunner.log" and print it.

    Args:
        msg (str): Message to be saved in the log file "dscfrunner.log" and printed.
    """
    with open("dscfrunner.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

