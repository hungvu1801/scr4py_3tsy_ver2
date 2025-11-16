from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Optional

from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils.action_utils import scroll_to_elem
from src.utils.decorators import selenium_exception_handler
from .elems import CanvaElems

logger = setup_logger(name="CanvasLog", log_dir=f"{LOG_DIR}/canvas_logs")


class CanvaService:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.img = None
        # self.current_img: int = 1
        self.number_of_processed_imgs: int = 0
        self.processed_img = list()

    @selenium_exception_handler
    def go_to_main_site(self, project_url: str) -> int:
        logger.info("go_to_main_site")
        self.driver.get(project_url)
        self.driver.implicitly_wait(10)
        time.sleep(1)
        return 1

    def increment_cur_img(self, step: int = 1) -> None:
        # self.current_img += (step + 1)
        self.number_of_processed_imgs += 1

    def reset_cur_img(self) -> None:
        # self.current_img = 1
        self.number_of_processed_imgs = 0
        self.processed_img.clear()

    @selenium_exception_handler
    def find_img_elem(self, filter_edit: bool = True) -> int:
        logger.info("find_img_elem")
        time.sleep(2)
        img_lst = WebDriverWait(self.driver, 50).until(
            EC.presence_of_all_elements_located((By.XPATH, CanvaElems.IMG_ELEM))
        )
        has_img = 0
        for img in img_lst:
            img_name = img.find_element(By.XPATH, CanvaElems.IMG_NAME).text
            if filter_edit:
                if (
                    img_name not in self.processed_img
                    and "edit" not in img_name.lower()
                ):
                    has_img = 1
                    self.img = img
                    self.processed_img.append(img_name)
                    scroll_to_elem(self.driver, self.img)
                    break
            else:
                if img_name not in self.processed_img and "edit" in img_name.lower():
                    has_img = 1
                    self.img = img
                    self.processed_img.append(img_name)
                    scroll_to_elem(self.driver, self.img)
                    break

        time.sleep(1)
        return has_img

    def count_img_processed(self) -> None:
        print(f"Total images processed: {len(self.processed_img)}")

    # @selenium_exception_handler
    def get_img_name(self) -> Optional[str]:
        logger.info("get_img_name")
        try:
            img_name = self.img.find_element(By.XPATH, CanvaElems.IMG_NAME).text
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
    def click_img_menu(self) -> int:
        logger.info("click_img_menu")
        time.sleep(1)
        self.img.find_element(By.XPATH, CanvaElems.IMG_MENU).click()
        time.sleep(1)
        return 1

    @selenium_exception_handler
    def click_edit_img(self) -> int:
        logger.info("click_edit_img")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.EDIT_IMG_BTN))
        ).click()
        time.sleep(1)

    @selenium_exception_handler
    def click_download_img(self) -> None:
        logger.info("click_download_img")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.DOWNLOAD_IMG_BTN))
        ).click()
        time.sleep(1.5)

    @selenium_exception_handler
    def click_remove_bg(self) -> None:
        logger.info("click_remove_bg")
        time.sleep(2.5)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.REMOVE_BG_BTN))
        ).click()
        time.sleep(1.5)

    @selenium_exception_handler
    def is_finished_remove_bg(self) -> bool:
        logger.info("is_finished_remove_bg")
        save_btn = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.SAVE_BTN))
        )
        return save_btn.get_attribute("aria-disabled") is None

    @selenium_exception_handler
    def check_is_finished_remove_bg(self) -> None:
        logger.info("check_is_finished_remove_bg")
        while True:
            if self.is_finished_remove_bg():
                break
            time.sleep(2)

    def check_if_can_remove_bg(self) -> bool:
        logger.info("check_if_can_remove_bg")
        can_rm = True
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, CanvaElems.NOTE_CANNOT_REMOVE_BG)
                )
            )
            can_rm = False
        except Exception as e:
            logger.info(f"Error in check_if_can_remove_bg {e}")
            pass
        finally:
            return can_rm

    @selenium_exception_handler
    def save_img(self) -> None:
        logger.info("save_img")
        save_btn = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.SAVE_BTN))
        )

        if save_btn.get_attribute("aria-disabled") == "true":
            return 0

        save_btn.click()

        time.sleep(3)
        return 1

    @selenium_exception_handler
    def close_img(self) -> None:
        logger.info("close_img")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, CanvaElems.CLOSE_BTN))
        ).click()
        logger.info(
            f"Skipped image that can not remove background: {self.get_img_name()}"
        )
        time.sleep(1)

    def refresh_page(self) -> None:
        logger.info("refresh_page")
        self.driver.refresh()
        time.sleep(5)

    # def scroll_page(self):
    #     logger.info("scroll_page")

    #     scroll_page_down(self.driver, height=None, SCROLL_PAUSE_TIME=3)
    #     #scroll to the top
    #     scroll_to_elem(driver=self.driver, new_position=0)
    #     time.sleep(4)

    def execute_remove_bg(self, project_url: str) -> None:
        self.go_to_main_site(project_url)
        while True:
            try:
                if not self.find_img_elem():
                    break
                logger.info(
                    f"Processing image number: {self.number_of_processed_imgs + 1}"
                )
                self.count_img_processed()

                if not self.click_img_menu():
                    continue
                self.click_edit_img()
                self.click_remove_bg()
                if not self.check_if_can_remove_bg():
                    self.increment_cur_img()
                    self.close_img()
                    continue
                self.check_is_finished_remove_bg()
                if not self.save_img():
                    self.close_img()
                    continue
                self.increment_cur_img()
            except Exception as e:
                logger.error(f"Error in execute loop: {e}")
                continue
        logger.info(
            f"Done processing -- total images processed: {self.number_of_processed_imgs}"
        )

    def execute_download_edited(self, project_url: str = None) -> None:
        logger.info("execute_download_edited")
        if project_url:
            self.go_to_main_site(project_url)
        else:
            self.reset_cur_img()
            self.refresh_page()
        while True:
            try:
                if not self.find_img_elem(filter_edit=False):
                    break
                self.click_img_menu()
                self.click_download_img()

                self.increment_cur_img(step=0)
            except Exception as e:
                logger.error(f"Error in execute loop: {e}")
                continue

    def execute(self, project_url: str) -> None:
        self.execute_remove_bg(project_url=project_url)
        self.execute_download_edited()
