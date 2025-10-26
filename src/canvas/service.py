from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from src.creative_fabrica.config import *
from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils.action_utils import scroll_to_elem
from src.utils.decorators import selenium_exception_handler
from .config import PROJECT_URL
from .elems import CanvasElems
from src.utils.action_utils import scroll_to_elem


logger = setup_logger(name="CanvasLog", log_dir=f"{LOG_DIR}/canvas_logs")

class RemoveBGService:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.img = None
        self.current_img: int = 1

    @selenium_exception_handler
    def go_to_main_site(self) -> int:
        logger.info("go_to_main_site")
        self.driver.get(PROJECT_URL)
        self.driver.implicitly_wait(10)
        time.sleep(1)
        return 1
    
    def increment_cur_img(self):
        self.current_img += 2

    @selenium_exception_handler
    def find_img_elem_by_num(self) -> int:
        time.sleep(2)
        self.img = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.IMG_ELEM.format(number=self.current_img))))
        time.sleep(1)
        return 1

    @selenium_exception_handler
    def click_img_menu(self):
        scroll_to_elem(self.driver, CanvasElems.IMG_ELEM.format(number=self.current_img))
        WebDriverWait(self.img, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.IMG_MENU))).click()
        time.sleep(1)

    @selenium_exception_handler
    def click_edit_img(self):
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.EDIT_IMG_BTN))).click()
        time.sleep(1)
    
    
    @selenium_exception_handler
    def click_remove_bg(self):
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.REMOVE_BG_BTN))).click()
        time.sleep(1)


    @selenium_exception_handler
    def is_finished_remove_bg(self) -> bool:
        save_btn = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.SAVE_BTN)))
        return save_btn.get_attribute("aria-disabled") == None

    def check_is_finished_remove_bg(self):
        while True:
            if self.is_finished_remove_bg():
                break
            time.sleep(2)

    @selenium_exception_handler
    def save_img(self):
        save_btn = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located(
                (By.XPATH, CanvasElems.SAVE_BTN)))
        save_btn.click()
        time.sleep(1)

    def main(self):
        self.go_to_main_site()
        while True:
            if not self.find_img_elem_by_num():
                break
            self.click_img_menu()
            self.click_edit_img()
            self.click_remove_bg()
            self.check_is_finished_remove_bg()
            self.save_img()
