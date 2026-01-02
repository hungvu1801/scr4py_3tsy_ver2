from dotenv import load_dotenv
import os
import re
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


from src.utils.utils import download_directly_with_selenium
from src.ideogram.IdeoElems import IdeoElems
from src.logger import setup_logger
from src.settings import IDEOGRAM_URL, LOG_DIR, IMAGE_DOWNLOAD
from src.assets import design_dict


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

logger = setup_logger(name="IdeogramLoggerService", log_dir=f"{LOG_DIR}/ideogram_logs")


def check_default_settings(driver: webdriver.Chrome) -> None:
    logger.info("Checking default settings for Ideogram.")
    check_ratio(driver)
    check_num_of_imgs(driver)
    check_design(driver)


def browse_site(driver: webdriver.Chrome) -> None:
    """
    Open the specified URL in the provided Selenium WebDriver instance.
    """
    try:
        logger.info(f"Browsing site: {IDEOGRAM_URL}")
        driver.get(IDEOGRAM_URL)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.main_text_box))
        ).click()
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


def wait_for_generation(driver: webdriver.Chrome) -> int:
    logger.info("Waiting for image generation to complete.")
    wait_time_count = 0
    attempt = 0
    try:
        # wait for policy
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.policy_elem))
        )
        return -1
    except TimeoutException:
        logger.info("There are not policy.")
    while True:
        try:
            p_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, IdeoElems.generating_notifier)
                )
            )

            while p_elem.text != "Generation complete":
                time.sleep(5)
                wait_time_count += 5
                logger.info(f"Waiting for image generation : {wait_time_count} seconds")
                p_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, IdeoElems.generating_notifier)
                    )
                )
            return 1
        except TimeoutException as e:
            logger.error(
                f"Timeout while waiting for the image generation to complete. {e}"
            )
            time.sleep(5)
        except StaleElementReferenceException as e:
            logger.error(
                f"StaleElement while waiting for the image generation to complete. {e}"
            )
            time.sleep(5)
        except Exception as e:
            if attempt == 3:
                logger.error(
                    f"Error while waiting for the image generation to complete. {e} \nEscaping ..."
                )
                return 0
            attempt += 1
            logger.error(
                f"Error while waiting for the image generation to complete. {e}\nAttempt = {attempt}"
            )
            time.sleep(5)


def get_image_urls(driver: webdriver.Chrome):
    logger.info("Getting image URLs from Ideogram.")
    try:
        img_elems = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, IdeoElems.img_elems))
        )

    except TimeoutException as e:
        logger.error(f"Timeout while waiting for image elements: {str(e)}")
        return None

    for img_elem in img_elems:
        try:
            time.sleep(3)
            url_img = img_elem.find_element(By.XPATH, ".//img").get_attribute("src")
            yield url_img
        except Exception as e:
            logger.error(f"Error while downloading image: {str(e)}")
            yield None


def generate_image(
    driver_gen: webdriver.Chrome,
    driver_down: webdriver.Chrome,
    prompt: str,
    sku_name: str,
) -> int:
    logger.info(f"Generating image with SKU name: {sku_name}")
    if not prompt:
        return 0
    ## Send prompt to the text area and click the generate button
    while True:
        try:
            text_area = driver_gen.find_element(By.XPATH, IdeoElems.main_text_box)
            text_area.send_keys(Keys.CONTROL, "a")
            text_area.send_keys(Keys.DELETE)
            time.sleep(1)
            text_area.send_keys(prompt)
            time.sleep(3)
            break
        except Exception as e:
            logger.error(f"Error in locating Describe what you want to see: {str(e)}")
            time.sleep(1)
            continue

    while True:
        try:
            generate_button = driver_gen.find_element(
                By.XPATH, IdeoElems.generate_button
            )
            generate_button.click()
            time.sleep(1)
            break
        except Exception as e:
            logger.error(f"Error in locating Generation button: {str(e)}")
            time.sleep(1)
            continue

    ## Wait for the image generation to complete
    result_wait = wait_for_generation(driver_gen)
    if result_wait == -1:
        logger.info("Image generation blocked by policy.")
        return 1
    elif result_wait == 0:
        logger.error("Image generation failed, timed out or policy errors.")
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
                save_path = os.path.join(
                    IMAGE_DOWNLOAD, f"{sku_name}_{chr(suffix)}.png"
                )

                download_directly_with_selenium(
                    driver=driver_down, url=url_img, save_path=save_path
                )

                suffix += 1
            except StopIteration:
                logger.info("Img generator is depleted.")
                break
        return 1
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        return 0


def check_ratio(driver: webdriver.Chrome) -> None:
    logger.info("Checking ratio settings for Ideogram.")
    ratio_checking = os.environ.get("RESOLUTION_SETTINGS")
    width = os.environ.get("WIDTH").strip()
    height = os.environ.get("HEIGHT").strip()
    try:
        ratio_elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_elem))
        )
    except TimeoutException:
        return None
    ratio_checked = ratio_elem.text
    if ratio_checking != ratio_checked:
        # Click ratio button
        settings_ratio(driver, height, width)
    else:
        return None

    while True:
        try:
            ratio_elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_elem))
            )
        except TimeoutException:
            return None
        ratio_checked = ratio_elem.text
        if ratio_checking != ratio_checked:
            # Click ratio button
            settings_ratio(driver, height, width)
        else:
            return None


def settings_ratio(driver: webdriver.Chrome, height: str, width: str) -> None:
    logger.info(f"Setting ratio to {height}x{width} for Ideogram.")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_elem))
        ).click()
        # driver.find_element(
        #     By.XPATH, "//div[@class='MuiBox-root css-1dktxqu']/div[3]").click()
        time.sleep(1)
        # Click this to activate the input button
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, IdeoElems.ratio_elem_width_clickable)
            )
        ).click()
        time.sleep(1)
        # input width
        input_width = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_input_width))
        )
        text_len = len(input_width.get_attribute("value"))
        input_width.send_keys(Keys.END)  # move cursor to end
        for _ in range(text_len):
            input_width.send_keys(Keys.BACKSPACE)
        # input_width.send_keys("delete")
        time.sleep(2)
        input_width.send_keys(width)

        # input height
        input_height = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_input_heigth))
        )

        text_len = len(input_height.get_attribute("value"))
        input_height.send_keys(Keys.END)
        for _ in range(text_len):
            input_height.send_keys(Keys.BACKSPACE)

        time.sleep(1)
        input_height.send_keys(height)

        # Save
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.ratio_save_btn))
        ).click()

        time.sleep(1)
    except StaleElementReferenceException as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")
    except TimeoutException as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")
    except Exception as e:
        logger.error(f"Error while checking or setting ratio: {str(e)}")


def check_num_of_imgs(driver: webdriver.Chrome) -> None:
    logger.info("Checking number of images settings for Ideogram.")
    image_num = os.environ.get("NUMIMG", "2")

    text_str = (
        WebDriverWait(driver, 10)
        .until(EC.presence_of_element_located((By.XPATH, IdeoElems.image_num_elem)))
        .text
    )

    try:
        image_num_checked = re.search(r"(\d+)$", text_str).group(1)
    except AttributeError:
        logger.error("Could not find the number of images in the text.")
        return None
    if image_num != image_num_checked:
        settings_num_of_imgs(driver, image_num)
    else:
        return None


def settings_num_of_imgs(driver: webdriver.Chrome, image_num: str = "2") -> None:
    logger.info(f"Setting number of images to {image_num} for Ideogram.")
    try:
        # Click on image settings tab
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.image_num_elem))
        ).click()

        time.sleep(1)
        # Click on number of images button
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, IdeoElems.image_num_elem_btn.format(image_num=image_num))
            )
        ).click()

        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.image_num_elem))
        ).click()

        time.sleep(1)
    except Exception as e:
        logger.error(f"Error while checking or setting ratio: {e}")


def check_design(driver: webdriver.Chrome) -> None:
    logger.info("Checking design settings for Ideogram.")
    try:
        # Check if the design is set
        design = os.environ.get("DESIGN", "Design")
        design_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.design_elem))
        )
        if design_elem.text == design:
            logger.info("Design is already set.")
            return
        else:
            settings_design(driver, design)
    except Exception as e:
        logger.error(f"Error while checking or setting design: {e}")


def settings_design(driver: webdriver.Chrome, design: str) -> None:
    logger.info(f"Setting design to {design} for Ideogram.")
    try:
        # Click on design settings tab
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, IdeoElems.design_elem))
        ).click()
        time.sleep(1)
        # Click on design button

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, IdeoElems.design_elem_btn.format(design=design_dict[design]))
            )
        ).click()

        time.sleep(1)
        # driver.find_element(
        #     By.XPATH, IdeoElems.design_elem).click()
        # time.sleep(1)
    except Exception as e:
        logger.error(f"Error while checking or setting design: {e}")
