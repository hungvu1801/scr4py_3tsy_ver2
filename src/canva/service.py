from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Optional
from src.creative_fabrica.config import *
from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils.action_utils import scroll_to_elem
from src.utils.decorators import selenium_exception_handler
from .elems import CanvaElems
from src.utils.action_utils import scroll_to_elem


logger = setup_logger(name="CanvasLog", log_dir=f"{LOG_DIR}/canvas_logs")

class CanvaService:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.img = None
        self.current_img: int = 1
        self.number_of_processed_imgs: int = 0

    @selenium_exception_handler
    def go_to_main_site(self, project_url: str) -> int:
        logger.info("go_to_main_site")
        self.driver.get(project_url)
        self.driver.implicitly_wait(10)
        time.sleep(1)
        return 1
    
    def increment_cur_img(self, step: int = 1) -> None:
        self.current_img += (step + 1)
        self.number_of_processed_imgs += 1

    def reset_cur_img(self) -> None:
        self.current_img = 1
        self.number_of_processed_imgs = 0

    @selenium_exception_handler
    def find_img_elem_by_num(self) -> int:
        logger.info("find_img_elem_by_num")
        time.sleep(2)
        self.img = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.IMG_ELEM.format(number=self.current_img))))
        scroll_to_elem(self.driver, self.img)

        time.sleep(1)
        return 1

    # @selenium_exception_handler
    def get_img_name(self) -> Optional[str]:
        logger.info("get_img_name")
        try:
            time.sleep(1)
            img_name = self.img.find_element(By.XPATH, CanvaElems.IMG_NAME).text
            logger.info(f"{self.current_img} -- img_name: {img_name}")
            time.sleep(1)
            return img_name
        except Exception as e:
            logger.error(f"Error in get_img_name: {e}")
            return 

    def is_name_contains_edit(self, name: str) -> bool:
        logger.info("is_name_contains_edit")
        if "edit" in name.lower():
            return True
        return False
    
    @selenium_exception_handler
    def click_img_menu(self):
        logger.info("click_img_menu")
        time.sleep(1)
        self.img.find_element(By.XPATH, CanvaElems.IMG_MENU).click()
        # WebDriverWait(self.img, 50).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, CanvaElems.IMG_MENU))).click()
        time.sleep(1)

    @selenium_exception_handler
    def click_edit_img(self):
        logger.info("click_edit_img")
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.EDIT_IMG_BTN))).click()
        time.sleep(1)
    
    @selenium_exception_handler
    def click_download_img(self):
        logger.info("click_download_img")
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.DOWNLOAD_IMG_BTN))).click()
        time.sleep(1)

    @selenium_exception_handler
    def click_remove_bg(self):
        logger.info("click_remove_bg")
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.REMOVE_BG_BTN))).click()
        time.sleep(1)


    @selenium_exception_handler
    def is_finished_remove_bg(self) -> bool:
        logger.info("is_finished_remove_bg")
        save_btn = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.SAVE_BTN)))
        return save_btn.get_attribute("aria-disabled") == None
    
    @selenium_exception_handler
    def check_is_finished_remove_bg(self):
        logger.info("check_is_finished_remove_bg")
        try:
            while True:
                if self.is_finished_remove_bg():
                    break
                time.sleep(2)
        except Exception as e:
            logger.error(f"Error in check_is_finished_remove_bg: {e}")

    @selenium_exception_handler
    def save_img(self):
        logger.info("save_img")
        save_btn = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvaElems.SAVE_BTN)))
        save_btn.click()
        time.sleep(3)

    def execute(self, project_url: str) -> None:
        self.go_to_main_site(project_url)
        while True:
            try:
                if not self.find_img_elem_by_num():
                    break
                logger.info(f"Processing image number: {self.current_img}")
                self.click_img_menu()
                self.click_edit_img()
                self.click_remove_bg()
                self.check_is_finished_remove_bg()
                self.save_img()
                self.increment_cur_img()
            except Exception as e:
                logger.error(f"Error in execute loop: {e}")
                break
        logger.info(f"Done processing -- total images processed: {self.number_of_processed_imgs}")
        self.reset_cur_img()
        while True:
            self.find_img_elem_by_num()
            name = self.get_img_name()
            if name and self.is_name_contains_edit(name):
                self.click_img_menu()
                self.click_download_img()
            else:
                break
            self.increment_cur_img(step=0)
