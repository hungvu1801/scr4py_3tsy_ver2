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
        return 1

class GoToAccount(UploadState):
    def handle(self) -> int:
        logger.info("go_to_account")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ACCOUNT_BTN))
        ).click()
        time.sleep(1)
        return 1

class GoToPortal(UploadState): 
    def handle(self) -> int:
        logger.info("go_to_portal")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ACC_VENDOR_PROTAL))
        ).click()
        time.sleep(1)
        return 1
    
class ClickAddProd(UploadState):
    def handle(self) -> int:
        logger.info("click_add_prod")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ADD_PRODUCT))
        ).click()
        # Check for page title "Add a New product"
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.PAGE_TITLE))
        )
        time.sleep(1)
        return 1

class WriteProductName(UploadState): 
    def handle(self) -> int:
        logger.info("write_product_name")
        time.sleep(5)
        while True:
            try:
                product_name = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, SofontsyElems.PRODUCT))
                )
                if product_name:
                    break
            except Exception as e:
                print(e)
                self.driver.refresh()
                print("Waiting for product name")
                logger.info("Waiting for product name")
                time.sleep(5)
        scroll_to_elem(self.driver, product_name)
        product_name.click()
        write_with_delay(
            element=product_name, message=self.current_item.title, interval=0.01
        )
        return 1

class ClickAddProduct(UploadState): 
    def handle(self) -> int: 
        logger.info("click_add_prod")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ADD_PRODUCT))
        ).click()
        # Check for page title "Add a New product"
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.PAGE_TITLE))
        )
        time.sleep(1)
        return 1

class WritePrice(UploadState): 
    def handle(self) -> int:
        logger.info("write_price")
        time.sleep(1)
        price = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.PRICE))
        )
        scroll_to_elem(self.driver, price)
        price.click()
        time.sleep(1)
        write_with_delay(element=price, message=self.current_item.price)
        com_price = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.COMPARE_PRICE))
        )
        com_price.click()
        time.sleep(1)
        write_with_delay(element=price, message=self.current_item.com_price)
        return 1

class WriteDescription(UploadState): 
    def handle(self) -> int:
        logger.info("write_description")
        time.sleep(1)
        description = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.DESCRIPTION))
        )
        scroll_to_elem(self.driver, description)
        description.click()
        time.sleep(1)
        write_with_delay(
            element=description, message=self.current_item.description, interval=0.005
        )
        return 1

class WriteTags(UploadState): 
    def handle(self) -> int:
        logger.info("write_tags")
        time.sleep(1)
        tags = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.TAGS))
        )
        scroll_to_elem(self.driver, tags)
        tags.click()
        time.sleep(1)
        write_with_delay(element=tags, message=self.current_item.tag, interval=0.005)
        return 1

class UploadImgs(UploadState): 
    def handle(self) -> int:
        logger.info("upload_imgs")
        time.sleep(1)
        upload_img = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.UPLOAD_PRODUCT_IMGS)
            )
        )
        scroll_to_elem(self.driver, upload_img)
        for img in self.current_item.img_files:
            upload_img_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, SofontsyElems.UPLOAD_PRODUCT_IMGS_INPUT)
                )
            )
            time.sleep(1.5)
            upload_img_input.send_keys(img)
            time.sleep(1)
        return 1

class UploadZip(UploadState): 
    def handle(self) -> int:
        logger.info("upload_zip")
        time.sleep(1)
        upload_zip = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.UPLOAD_PRODUCT_FILE)
            )
        )
        upload_zip_input = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.UPLOAD_PRODUCT_FILE_INPUT)
            )
        )
        scroll_to_elem(self.driver, upload_zip)
        upload_zip_input.send_keys(self.current_item.zip_file)
        time.sleep(1.5)
        return 1

class Clicksubmit(UploadState): 
    def handle(self) -> int:
        logger.info("click_submit")
        time.sleep(5)
        while True:
            try:
                submit = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, SofontsyElems.SUBMIT))
                )
                if submit:
                    break
            except Exception as e:
                print(e)
                time.sleep(5)
        scroll_to_elem(self.driver, submit)
        time.sleep(1)
        while True:
            try:
                submit.click()
                time.sleep(1.5)

                submit = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, SofontsyElems.SUBMIT))
                )
                if submit:
                    continue
                else:
                    break
            except Exception:
                break
        return 1
