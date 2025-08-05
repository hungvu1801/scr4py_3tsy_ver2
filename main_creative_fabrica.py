import sys
import os
import argparse
from src.utils.load_env import *
from src.creative_fabrica.controller import controller




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run controller with selected profiles.")
    parser.add_argument(
        "--profile", 
        nargs="+", 
        choices=["1", "2", "3", "4"], 
        required=True,
        help="Specify which profile(s) to run (e.g., --profile 1 2 3 4)"
    )
    args = parser.parse_args()

    controller(profile_id=args.profile[0])