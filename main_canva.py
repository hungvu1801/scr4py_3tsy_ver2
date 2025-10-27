import argparse
from src.utils.load_env import *
from src.canva.controller import Controller




if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Run controller with selected profiles.")
    # parser.add_argument(
    #     "--profile", 
    #     nargs="+", 
    #     choices=["1", "2", "3", "4"], 
    #     required=True,
    #     help="Specify which profile(s) to run (e.g., --profile 1 2 3 4)"
    # )

    # args = parser.parse_args()
    # controller = Controller(profile_id=args.profile[0])
    controller = Controller(profile_id="1")
    controller.main()
    