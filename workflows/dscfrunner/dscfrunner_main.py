#!/usr/bin/env python3
"""Main routine of the dscfrunner."""
from __future__ import annotations
from dscfrunner_parser import parse_arguments_dscfrunner
from dscfrunner_functions import *


def dscfrunner_main() -> None:
    """Main function for dscfrunner. Parses arguments and calls the appropriate functions.
    """
    # read command line flags and set them
    args = parse_arguments_dscfrunner()
    XYZ        = args.xyz
    TD_INP     = args.tdinp
    GUESS_INP  = args.guessinp
    DSCF_INP   = args.dscfinp
    TDOPT_INP  = args.tdoptinp
    STATE      = args.state
    THRESHOLD  = args.threshold
    TDFALLBACK = args.tdfallback

    # print the settings into the log file
    log("Workflow configuration:")
    log(f"  xyz        : {XYZ}")
    log(f"  TD input   : {TD_INP}")
    log(f"  Guess input: {GUESS_INP}")
    log(f"  dSCF input : {DSCF_INP}")
    log(f"  TDopt input: {TDOPT_INP}")
    log(f"  state      : S{STATE}")
    log(f"  threshold  : {THRESHOLD}")
    log(f"  td fallback: {TDFALLBACK}")



    # starting with the TDDFT SP calculation
    log("Starting workflow")

    if is_done("td.out"):
        log("td.out already exists and is valid → skipping TDDFT SP")
    else:
        run_orca(TD_INP, "td.out")

    if not terminated_successfully("td.out"):
        log("TDDFT SP failed. Stopping.")
        sys.exit(1)



    # check the weights of the configurations
    #weights = parse_tddft_weights("td.out", state=STATE)
    #if not weights:
    #    log("No TDDFT weights found. Stopping.")
    #    sys.exit(1)
    #maxw = max(weights)
    #log(f"Max config weight: {maxw:.2f}")


    # read out the tddft excitations and their weights for the desired state
    excs = parse_tddft_excitations("td.out", state=STATE)
    occ, virt, weight = dominant_excitation(excs)
    log(f"Dominant excitation: {occ} → {virt} (weight={weight:.2f})")


    # check if the case is single - or multi-configurational
    if weight >= THRESHOLD:
        log("Single-config case → trying dSCF")

        if is_done("dscf.out"):
            log("dscf.out already exists and is valid → skipping dSCF")
            log("Workflow finished.")
            sys.exit(0)

        # perform a DeltaSCF calculation for the single-configurational case

        # find out the index of the homo = largest index of occ 
        homo = get_homo_index(excs)
        log(f"HOMO index = {homo}")
        # build the occupation vector for alphaconf in dscf input
        alphaconf = build_alphaconf(occ, virt, homo)
        log(f"Using alphaconf = {alphaconf}")
        # update the DeltaSCF input file
        update_alphaconf_in_input(DSCF_INP, alphaconf)

        # run the calculation
        log("Running dSCF")
        run_orca(GUESS_INP, "guess.out")
        run_orca(DSCF_INP, "dscf.out")

        if terminated_successfully("dscf.out"):
            log("dSCF finished successfully.")
            log("Workflow finished.")
            sys.exit(0)

        if not TDFALLBACK:
            log("dSCF failed and TDDFT fallback disabled.")
            sys.exit(1)

        log("dSCF failed → fallback to TDDFT optimization")


    # perform a TDDFT OPT+FREQ calculation if the case is multi-configurational or if the previous DeltaSCF calculation did not terminate sucessfully
    if is_done("tdopt.out"):
        log("tdopt.out already exists and is valid → skipping TDDFT optimization")
    else:
        log("Running TDDFT optimization")
        run_orca(TDOPT_INP, "tdopt.out")

        

    if not terminated_successfully("tdopt.out"):
        log("TDDFT optimization failed.")
        sys.exit(1)

    log("TDDFT optimization finished successfully.")
    log("Workflow finished.")



if __name__ == "__main__":

    dscfrunner_main()


