import argparse
from src.utils.load_env import *
from src.canva.controller import Controller




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run controller with selected profiles.")
    parser.add_argument(
        "-p","--profile", 
        nargs="+", 
        choices=["1", "2", "3", "4"], 
        required=True,
        help="Specify which profile(s) to run (e.g., --profile 1 2 3 4)"
    )
    parser.add_argument(
        "-u", "--project-url",
        type=str,
        required=True,
        help="Specify project file (e.g., --project-url https://www.canva.com/folder/FAF3D1dlNTc)"
    )

    args = parser.parse_args()
    controller = Controller(profile_id=args.profile[0], project_url=args.project_url)
    # controller = Controller(profile_id="1", project_url="https://www.canva.com/folder/FAF3D1dlNTc")
    controller.main()
    