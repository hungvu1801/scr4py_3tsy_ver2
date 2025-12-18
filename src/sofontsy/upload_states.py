from src.sofontsy.abstract import UploadState
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time
from typing import Optional
from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils.action_utils import write_with_delay, scroll_to_elem
from src.utils.decorators import selenium_exception_handler
from .config import BASE_URL
from .elems import SofontsyElems, SofontsyItems

logger = setup_logger(name="SofonsyLog", log_dir=f"{LOG_DIR}/sofontsy_logs")


class GoToMainSite(UploadState):
    def handle(self) -> int:
        logger.info("go_to_main_site")
        self.driver.get(BASE_URL)
        self.driver.implicitly_wait(10)
        time.sleep(1)


class GoToAccount(UploadState):
    def handle(self) -> int:
        logger.info("go_to_account")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ACCOUNT_BTN))
        ).click()
        time.sleep(1)


class GoToPortal(UploadState): ...
