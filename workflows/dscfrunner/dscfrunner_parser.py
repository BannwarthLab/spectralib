"""Contains function to parse command line arguments."""
from __future__ import annotations
import argparse


def parse_arguments_dscfrunner():
    """Read command line arguments and store them for further processing.
      
    Returns:
        args (argparse.Namespace): Object storing all commandline arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "xyz",
        help="Coordinate file (xyz format)"
    )

    # optional inputs
    parser.add_argument(
        "--tdinp",
        default="td.inp",
        help="TDDFT single-point input file (default: td.inp)"
    )

    parser.add_argument(
        "--guessinp",
        default="guess.inp",
        help="Guess input file for dSCF (default: guess.inp)"
    )

    parser.add_argument(
        "--dscfinp",
        default="dscf.inp",
        help="dSCF optimization+freq input file (default: dscf.inp)"
    )

    parser.add_argument(
        "--tdoptinp",
        default="tdopt.inp",
        help="TDDFT optimization+freq input file (default: tdopt.inp)"
    )

    parser.add_argument(
        "--state",
        type=int,
        default=1,
        help="Excited state to analyze (default: 1)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Configuration weight threshold (default: 0.7)"
    )

    parser.add_argument(
        "--tdfallback",
        action="store_true",
        default=True,
        help="Fallback to TDDFT optimization if dSCF fails"
    )

    args = parser.parse_args()
    return args