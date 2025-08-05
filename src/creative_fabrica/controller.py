from concurrent.futures import ThreadPoolExecutor


import os
import sys
import re
from threading import Lock
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.logger import setup_logger
from src.settings import CREATIVE_DATA_DIR, LOG_DIR
from src.utils import utils
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.utils.load_env import *

from .service import UploadFile


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(f"{LOG_DIR}/cre_fab_logs", exist_ok=True)
os.makedirs(f"{CREATIVE_DATA_DIR}", exist_ok=True)

logger = setup_logger(name="CreativeFabricaLog", log_dir=f"{LOG_DIR}/cre_fab_logs")


def controller(profile_id) -> None:
    """
    This function serves as a placeholder for the controller logic.
    It currently does not perform any operations.
    """
    driver = open_gemlogin_driver(profile_id=profile_id)
    try:
        pipeline = UploadFile(driver=driver)
        if not driver:
            logger.error("Failed to open driver.")
            return

        df = utils.prompt_open_file()
        if df.empty:
            logger.error("DF Empty.. Exiting..")
            return
        item_gen = utils.generator_items(df)
        try:
            while True:
                item = next(item_gen)
                pipeline.set_current_item(item)
                pipeline.execute()
        except StopIteration:
            logger.info("All items processed successfully.")
        except Exception as e:
            logger.error(f"Error {e}")
            input()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Exiting gracefully.")
    finally:
        if driver:
            close_gemlogin_driver(driver)