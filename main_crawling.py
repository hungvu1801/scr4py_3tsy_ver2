import sys
import os
from dotenv import load_dotenv

from src.etsy.controller import controller_main
from src.settings import IMAGE_DOWNLOAD_ETSY

load_dotenv()

os.makedirs(IMAGE_DOWNLOAD_ETSY, exist_ok=True)

if __name__ == "__main__":
    controller_main()