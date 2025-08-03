

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Optional
from src.creative_fabrica.config import *
from src.logger import setup_logger
from src.settings import WAIT_TIME, LOG_DIR
from src.utils.action_utils import write_pyautogui, write_with_delay, scroll_to_elem
from src.utils.decorators import selenium_exception_handler
from .elems import CreateFabricaElems, CreateFabricaItems


logger = setup_logger(name="CreativeFabricaLog", log_dir=f"{LOG_DIR}/cre_fab_logs")

class UploadFile:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.current_item = None
        self.step = [
            self.get_sites,
            self.write_product_name,
            self.write_category,
            self.write_price,
            self.write_description,
            self.write_tags,
            self.upload_imgs,
            self.upload_zip,
            self.check_boxes,
            self.check_upload_status,
            self.click_submit,
            self.check_upload_completed
        ]
        self.url = f"{BASE_URL}{UPLOAD_SUFFIX}"

    def set_current_item(self, item: Optional[CreateFabricaItems]):
        self.current_item = item

    @selenium_exception_handler
    def get_sites(self) -> int:
        logger.info("get_sites")
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.PAGE_TITLE)))
        return 1
    
    def execute(self) -> int:
        for i, step in enumerate(self.step):
            if not step():
                logger.error(f"Pipeline failed at step {i + 1} ({step.__name__}).")
                return 0
        return 1

    @selenium_exception_handler
    def write_product_name(self) -> int:
        logger.info("write_product_name")
        time.sleep(1)
        product_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.PRODUCT)))
        scroll_to_elem(self.driver, product_name)
        product_name.click()
        write_with_delay(element=product_name, message=self.current_item.title, interval=0.01)
        return 1

    @selenium_exception_handler
    def write_category(self) -> int:
        logger.info("write_category")
        category = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.CATEGORY)))
        category.click()
        
        time.sleep(1)
        category_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.CATEGORY_INPUT)))
        category_input.click()
        write_with_delay(element=category_input, message=self.current_item.category, interval=0.01)
        category_input.send_keys(Keys.ENTER)
        return 1

    @selenium_exception_handler
    def write_price(self) -> int:
        logger.info("write_price")
        time.sleep(1)
        price = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.PRICE)))
        scroll_to_elem(self.driver, price)
        price.click()
        time.sleep(1)
        write_with_delay(element=price, message=self.current_item.price)
        return 1

    @selenium_exception_handler
    def write_description(self) -> int:
        logger.info("write_description")
        time.sleep(1)
        description = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.DESCRIPTION)))
        scroll_to_elem(self.driver, description)
        description.click()
        time.sleep(1)
        write_with_delay(element=description, message=self.current_item.description, interval=0.005)
        return 1

    @selenium_exception_handler
    def write_tags(self) -> int:
        logger.info("write_tags")
        time.sleep(1)
        tags = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.TAGS)))
        scroll_to_elem(self.driver, tags)
        tags.click()
        time.sleep(1)
        write_with_delay(element=tags, message=self.current_item.tag, interval=0.005)
        return 1

    @selenium_exception_handler
    def upload_imgs(self) -> int:
        logger.info("upload_imgs")
        time.sleep(1)
        upload_img = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.UPLOAD_PRODUCT_IMGS)))
        scroll_to_elem(self.driver, upload_img)
        for img in self.current_item.img_files:
            upload_img_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, CreateFabricaElems.UPLOAD_PRODUCT_IMGS_INPUT)))
            time.sleep(1.5)
            upload_img_input.send_keys(img)
            time.sleep(1)
        return 1

    @selenium_exception_handler
    def upload_zip(self) -> int:
        logger.info("upload_zip")
        time.sleep(1)
        upload_zip = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.UPLOAD_PRODUCT_FILE)))
        upload_zip_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.UPLOAD_PRODUCT_FILE_INPUT)))
        scroll_to_elem(self.driver, upload_zip)
        upload_zip_input.send_keys(self.current_item.zip_file)
        time.sleep(1.5)
        return 1

    @selenium_exception_handler
    def check_boxes(self) -> int:
        logger.info("check_boxes")
        time.sleep(1)
        freebie_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.CHECKBOX_FREEBIE)))
        scroll_to_elem(self.driver, freebie_box)
        time.sleep(0.5)
        freebie_box.click()
        
        deal_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.CHECKBOX_DEALS)))
        scroll_to_elem(self.driver, deal_box)
        time.sleep(0.5)
        deal_box.click()
        
        term_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.CHECKBOX_TERMS)))
        scroll_to_elem(self.driver, term_box)
        time.sleep(1)
        term_box.click()
        return 1

    @selenium_exception_handler
    def click_submit(self) -> int:
        logger.info("click_submit")
        time.sleep(1)
        submit = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, CreateFabricaElems.SUBMIT)))
        scroll_to_elem(self.driver, submit)
        time.sleep(0.5)
        submit.click()
        time.sleep(1)
        return 1
    
    @selenium_exception_handler
    def check_upload_status(self, timeout:int = 300) -> int:
        logger.info("check_upload_status")
        expected_upload = len(self.current_item.img_files) + 1 # Must upload all items in img_files and a zip file
        start_time = time.time()
        successful_uploads = 0
        while time.time() - start_time < timeout:
            statuses = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, CreateFabricaElems.UPLOAD_ITEMS_STATUS)))
            for status in statuses:
                if "success" in status.get_attribute("class"):
                    successful_uploads += 1
            if successful_uploads >= expected_upload:
                return 1
            time.sleep(5)
        logger.error(f"Upload status check timed out after {timeout} seconds")
        return 0
    
    @selenium_exception_handler
    def check_upload_completed(self, timeout:int = 300) -> int:
        logger.info("check_upload_completed")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.driver.current_url == SUCCESS_URL:
                return 1
            time.sleep(5)
        return 0
