from dotenv import load_dotenv

import os


import re

import sys
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from src.assets import update_cols_ideogram, update_cols_etsy
from src.utils.gg_utils import download_media
from src.utils.utils import download_directly_with_selenium

from src.logger import setup_logger
from src.settings import IDEOGRAM_URL, LOG_DIR, IMAGE_DOWNLOAD


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/ideogram_logs", exist_ok=True)

logger = setup_logger(name="IdeogramLoggerService", log_dir=f"{LOG_DIR}/ideogram_logs")


def check_default_settings(driver: webdriver.Chrome):
    logger.info("Checking default settings for Ideogram.")
    check_ratio(driver)
    check_num_of_imgs(driver)
    check_design(driver)


def browse_site(driver:webdriver.Chrome) -> None:
    """
    Open the specified URL in the provided Selenium WebDriver instance.
    """
    try:
        logger.info(f"Browsing site: {IDEOGRAM_URL}")
        driver.get(IDEOGRAM_URL)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, 
                "//textarea[@placeholder='Describe what you want to see']"))
                )
        time.sleep(5)
    except TimeoutException as e:
        logger.error(f"Error while browsing site {IDEOGRAM_URL}: {str(e)}")
        raise e

def get_data_to_scrape(data):
    logger.info("get_data_to_scrape: Extracting data to scrape from Ideogram.")
    if isinstance(data, dict):
        range_ = data.get("range", 0)
        values = data.get("values", [])
        if range_ and values:
            match = re.search(r"[A-Z](\d+):", range_)
            if not match:
                logger.error(f"Range format not recognized: {range_}")
                return None
            start_row = match.group(1)
            for idx, val in enumerate(values, start=int(start_row)):
                if not isinstance(val, list):
                    logger.error(f"Expected list for row values, got: {val}")
                    continue
                logger.info(f"idx : {idx}, val : {val}")
                yield (idx, val)
    return None

def wait_for_generation(driver:webdriver.Chrome) -> bool:
    logger.info("Waiting for image generation to complete.")
    wait_time_count = 0
    attempt = 0
    while True:
        try:
            p_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, 
                    "//p[@class='MuiTypography-root MuiTypography-body1 css-1ce06iw']")))
            
            while p_elem.text != "Generation complete":
                time.sleep(5)
                wait_time_count += 5
                logger.info(f"Waiting for image generation : {wait_time_count} seconds")
                p_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, 
                        "//p[@class='MuiTypography-root MuiTypography-body1 css-1ce06iw']")))
            return True
        except TimeoutException as e:
            logger.error(f"Timeout while waiting for the image generation to complete. {e}")
            time.sleep(5)
        except StaleElementReferenceException as e:
            logger.error(f"StaleElement while waiting for the image generation to complete. {e}")
            time.sleep(5)
        except Exception as e:
            if attempt == 3:
                logger.error(f"Error while waiting for the image generation to complete. {e} \nEscaping ...")
                return False
            attempt += 1
            logger.error(f"Error while waiting for the image generation to complete. {e}\nAttempt = {attempt}")
            time.sleep(5)

def get_image_urls(driver:webdriver.Chrome):
    logger.info("Getting image URLs from Ideogram.")
    try:
        img_elems = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, 
                     "//div[contains(@class, 'MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-1')]/div")))

    except TimeoutException as e:
        logger.error(f"Timeout while waiting for image elements: {str(e)}")
        return None
    for img_elem in img_elems:
        try:
            time.sleep(3)
            url_img = img_elem.find_element(
                By.XPATH, ".//img").get_attribute("src")
            yield url_img
        except Exception as e:
            logger.error(f"Error while downloading image: {str(e)}")
            yield None


def generate_image(
        driver_gen: webdriver.Chrome, 
        driver_down: webdriver.Chrome, 
        prompt: str, 
        sku_name: str) -> int:
    logger.info(f"Generating image with SKU name: {sku_name}")
    if not prompt:
        return 0
    ## Send prompt to the text area and click the generate button
    while True:
        try:
            text_area = driver_gen.find_element(
                By.XPATH, "//textarea[@placeholder='Describe what you want to see']"
                )
            text_area.send_keys(Keys.CONTROL, 'a')
            text_area.send_keys(Keys.DELETE)
            time.sleep(1)
            text_area.send_keys(prompt)
            time.sleep(1)
            break
        except Exception as e:
            logger.error(f"Error in locating Describe what you want to see: {str(e)}")
            time.sleep(1)
            continue
        
    while True:
        try:
            generate_button = driver_gen.find_element(
                By.XPATH, 
                "//button/span[contains(text(), 'Generate')]")
            generate_button.click()
            time.sleep(1)
            break
        except Exception as e:
            logger.error(f"Error in locating Generation button: {str(e)}")
            continue
    
    ## Wait for the image generation to complete
    if not wait_for_generation(driver_gen):
        logger.error("Image generation failed or timed out.")
        return 0
    try:
        url_img_generator = get_image_urls(driver_gen)
        # Get the first image URL
        suffix = 65
        while True:
            time.sleep(1)
            try:
                url_img = next(url_img_generator)
                logger.info(url_img)
                save_path = os.path.join(IMAGE_DOWNLOAD, f"{sku_name}_{chr(suffix)}.png")

                download_directly_with_selenium(
                    driver=driver_down, 
                    url=url_img, 
                    save_path=save_path)
            
                suffix += 1
            except StopIteration:
                logger.info("Img generator is depleted.")
                break
        return 1
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        return 0
    

def check_ratio(driver:webdriver.Chrome) -> None:
    logger.info("Checking ratio settings for Ideogram.")
    ratio_checking = os.environ.get("RESOLUTION_SETTINGS")
    width = int(os.environ.get("WIDTH"))
    heigth = int(os.environ.get("HEIGHT"))
    try:
        ratio_elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, 
                    "//div[@class='MuiBox-root css-1dktxqu']/div[3]"))
                    )
    except TimeoutException:
        return None
    ratio_checked = ratio_elem.text
    if ratio_checking != ratio_checked:
        # Click ratio button
        settings_ratio(driver, heigth, width)
    else:
        return None

def settings_ratio(driver:webdriver.Chrome, heigth, width) -> None:
    logger.info(f"Setting ratio to {heigth}x{width} for Ideogram.")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, 
                "//div[@class='MuiBox-root css-1dktxqu']/div[3]"))
                ).click()
        # driver.find_element(
        #     By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[3]").click()
        time.sleep(1)
        # Click custom button
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, 
                "//div[@class='MuiBox-root css-12lxzkk']/button[2]"))
                ).click()
        # driver.find_element(
        #     By.XPATH, "//div[@class='MuiBox-root css-12lxzkk']/button[2]").click()
        time.sleep(1)
        # input width
        input_width = driver.find_element(By.XPATH, "//div[@class='MuiBox-root css-125dcud']/div[1]/div[1]//input")
        
        input_width.send_keys("delete")
        time.sleep(2)
        input_width.send_keys(width)

        # input heigth
        input_height = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, 
                "//div[@class='MuiBox-root css-125dcud']/div[1]/div[2]//input"))
                )
        actions = ActionChains(driver)
        actions.double_click(input_height).perform()
        input_height.send_keys("delete")
        time.sleep(1)
        input_height.send_keys(height)

        # Save
        driver.find_element(By.XPATH, "//div[@class='MuiBox-root css-1ks2d2u']/button[2]").click()
        time.sleep(1)
    except StaleElementReferenceException as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")
    except TimeoutException as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")
    except Exception as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")

def check_num_of_imgs(driver:webdriver.Chrome) -> None:
    logger.info("Checking number of images settings for Ideogram.")
    image_num = os.environ.get("NUMIMG", "2")
    text = driver.find_element(
        By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[5]").text
    try:
        image_num_checked = re.search(r"(\d+)$", text).group(1)
    except AttributeError:
        logger.error("Could not find the number of images in the text.")
        return None
    if image_num != image_num_checked:
        settings_num_of_imgs(driver, image_num)
    else:
        return None

def settings_num_of_imgs(driver:webdriver.Chrome, image_num:str="1") -> None:
    logger.info(f"Setting number of images to {image_num} for Ideogram.")
    try:
        # Click on image settings tab
        driver.find_element(
            By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[5]").click()
        time.sleep(1)
        # Click on number of images button
        driver.find_element(
            By.XPATH, f"//div[@class='MuiToggleButtonGroup-root css-1mfgcko']/button[{image_num}]").click()
        time.sleep(1)
        driver.find_element(
            By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[5]").click()
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")

def check_design(driver:webdriver.Chrome) -> None:
    logger.info("Checking design settings for Ideogram.")
    try:
        # Check if the design is set
        design = os.environ.get("DESIGN", "Design")
        if not design:
            logger.error("Design is not set in the environment variables.")
            return
        else:
            settings_design(driver, design)
            logger.info("Design is already set.")
    except Exception as e:
        logger.error(f"Error while checking or setting design: {str(e)}")

def settings_design(driver:webdriver.Chrome, design:str) -> None:
    logger.info(f"Setting design to {design} for Ideogram.")
    try:
        # Click on design settings tab
        design_dict = {
            "Auto": 1,
            "Random": 2,
            "General": 3,
            "Realistic": 4,
            "Design": 5,
        }

        driver.find_element(
            By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[9]").click()
        time.sleep(1)
        # Click on design button
        driver.find_element(
            By.XPATH, f"//div[@class='MuiBox-root css-r7ft4d']/div[{design_dict[design]}]").click()
        time.sleep(1)
        driver.find_element(
            By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[9]").click()
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error while checking or setting design: {str(e)}")

