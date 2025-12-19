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


logger = setup_logger(name="CreativeFabricaLog", log_dir=f"{LOG_DIR}/sofontsy_logs")

class UploadFile:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.current_item = None
        self.init_steps = [
            self.go_to_main_site,
            self.go_to_account,
            self.go_to_portal,
        ]

        self.upload_steps = [
            self.click_add_prod,
            self.write_product_name,
            self.write_price,
            self.write_description,
            self.write_tags,
            self.upload_imgs,
            self.upload_zip,
            self.check_upload_status,
            self.click_submit,
            self.check_upload_completed,
        ]

    def set_current_item(self, item: Optional[SofontsyItems]):
        self.current_item = item

    @selenium_exception_handler
    def go_to_main_site(self) -> int:
        logger.info("go_to_main_site")
        self.driver.get(BASE_URL)
        self.driver.implicitly_wait(10)
        time.sleep(1)
        return 1

    @selenium_exception_handler
    def go_to_account(self) -> int:
        logger.info("go_to_account")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ACCOUNT_BTN))
        ).click()
        time.sleep(1)
        return 1

    @selenium_exception_handler
    def go_to_portal(self) -> int:
        logger.info("go_to_portal")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, SofontsyElems.ACC_VENDOR_PROTAL))
        ).click()
        time.sleep(1)
        return 1

    @selenium_exception_handler
    def click_add_prod(self) -> int:
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

    def execute(self, _type: str) -> int:
        if _type == "init":
            steps = self.init_steps
        elif _type == "upload":
            steps = self.upload_steps
        else:
            raise
        for i, step in enumerate(steps):
            if not step():
                logger.error(f"Pipeline failed at step {i + 1} ({step.__name__}).")
                return 0
        return 1

    @selenium_exception_handler
    def write_product_name(self) -> int:
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

    @selenium_exception_handler
    def write_price(self) -> int:
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

    @selenium_exception_handler
    def write_description(self) -> int:
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

    @selenium_exception_handler
    def write_tags(self) -> int:
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

    @selenium_exception_handler
    def upload_imgs(self) -> int:
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

    @selenium_exception_handler
    def upload_zip(self) -> int:
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

    @selenium_exception_handler
    def check_boxes(self) -> int:
        logger.info("check_boxes")
        time.sleep(1)
        freebie_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.CHECKBOX_FREEBIE)))
        scroll_to_elem(self.driver, freebie_box)
        time.sleep(0.5)
        freebie_box.click()
        
        deal_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.CHECKBOX_DEALS)))
        scroll_to_elem(self.driver, deal_box)
        time.sleep(0.5)
        deal_box.click()
        
        term_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, SofontsyElems.CHECKBOX_TERMS)))
        scroll_to_elem(self.driver, term_box)
        time.sleep(1)
        term_box.click()
        return 1

    @selenium_exception_handler
    def click_submit(self) -> int:
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

    @selenium_exception_handler
    def check_upload_status(self, timeout: int = 300) -> int: ...

    @selenium_exception_handler
    def check_upload_completed(self, timeout: int = 300) -> int: ...
