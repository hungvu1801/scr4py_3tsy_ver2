import os
from src.ideogram.controller import controller
from dotenv import load_dotenv
from src.settings import DATA_DOWNLOAD, LOG_DIR, IMAGE_DOWNLOAD, IMAGE_DOWNLOAD_SAMPLE
load_dotenv()

os.makedirs(DATA_DOWNLOAD, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(IMAGE_DOWNLOAD, exist_ok=True)
os.makedirs(IMAGE_DOWNLOAD_SAMPLE, exist_ok=True)

if __name__ == "__main__":
    controller()