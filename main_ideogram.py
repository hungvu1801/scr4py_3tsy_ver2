import os
from src.ideogram.controller import controller
from src.settings import DATA_DOWNLOAD, LOG_DIR, IMAGE_DOWNLOAD, IMAGE_DOWNLOAD_SAMPLE
import argparse


os.makedirs(DATA_DOWNLOAD, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(IMAGE_DOWNLOAD, exist_ok=True)
os.makedirs(IMAGE_DOWNLOAD_SAMPLE, exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run controller with selected profiles."
    )
    parser.add_argument(
        "--profile",
        type=int,
        nargs=2,
        required=True,
        help="Specify which profile(s) to run (e.g., --profile 6)",
    )
    parser.add_argument("--row", "-r", type=int, default=1, help="Starting row number")
    args = parser.parse_args()
    profile_1, profile_2 = args.profile
    controller(profile_1=profile_1, profile_2=profile_2, row_search=args.row)
