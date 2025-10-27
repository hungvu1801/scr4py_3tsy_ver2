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
    def go_to_main_site(self) -> int:
        logger.info("go_to_main_site")
        self.driver.get(PROJECT_URL)
        self.driver.implicitly_wait(10)
        time.sleep(1)
        return 1
    
    def increment_cur_img(self):
        self.current_img += 2
        self.number_of_processed_imgs += 1

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

    def execute(self):
        self.go_to_main_site()
        # input()
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
