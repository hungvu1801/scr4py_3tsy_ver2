import os
import sys
import random
import re
import time


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import Dict, List, Optional, Any
from src.assets import update_cols_etsy
from src.logger import setup_logger
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.GSheetWriteRead import GSheetWrite
from src.settings import ETSY_URL, WAIT_TIME, DATA_DOWNLOAD, LOG_DIR
from src.utils.utils import sku_generator, data_construct_for_gsheet


os.makedirs(f"{LOG_DIR}/etsy_logs", exist_ok=True)
logger = setup_logger(name="EtsyScraper", log_dir=f"{LOG_DIR}/etsy_logs")


def card_scraping(driver: webdriver.Chrome, url: str, store: str,) -> Dict[str, List]:
    """
    Scrape product cards from multiple pages.
    
    Args:
        driver: Chrome WebDriver instance
        url: Starting URL to scrape
        numpage: Maximum number of pages to scrape
        
    Returns:
        Dict containing product information
    """
    logger.info("In card scraping..")
    current_page = 0

    driver.get(url)
    # random_crawling(driver, is_card=True)
    time.sleep(random.uniform(2, 5))
    while True:
        try:
            nav_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, 
                    "//nav[@class='wt-hide-xs wt-show-lg category-nav-button-menu']"
                    )))
            if nav_elements:
                break
        except TimeoutException as e:
            logger.error(f"No navigation found")
        
        try:
            capchas = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, 
                            "//iframe[@title='DataDome Device Check']")))
            if capchas:
                time.sleep(10)
                driver.refresh()
        except TimeoutException as e:
            logger.error(f"No capcha found - Shop {store}")
            break

    
    data = {
        "img_url": []
    }
    # Store the parent window handle
    # parent_window = driver.current_window_handle
    while True:
        determined_crawling(driver=driver)
        current_page += 1

        #############################################################################################################
            # for i in range(len(items)):

        try:
            items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, 
                    "//div[contains(@class, 'responsive-listing-grid')]/div")))
        except TimeoutException as e:
            logger.error(f"Card craping error - Shop {store}")
            break
        for i, item in enumerate(items):
            try:
                item_img = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, ".//img"))).get_attribute("src")
                logger.info(f"image url found :{i} : {item_img}")
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", item)
                if not item_img:
                    logger.warning(f"No URL img found for item {i} on page {current_page}")
                    continue
                data["img_url"].append(item_img)

                # Scroll to item and click
                # items[i].click()
                time.sleep(random.uniform(2, 5))
            

            # Switch to new tab

            # chwd = driver.window_handles
            # for window in chwd:
            #     if window != parent_window:
            #         driver.switch_to.window(window)
            #         break
            
            # logger.info(f"Processing item {i}/{len(items)}: {item_url}")
            # product_datas = detail_scraping(driver=driver, url=item_url, store=store)
            
            # if product_datas:
            #     for product_data in product_datas:
            #         yield product_data
            
            except TimeoutException as e:
                logger.warning(f"Could not find link for item {i} on page {current_page}")
                continue
            except Exception as e:
                logger.error(f"Error processing item {i} on page {current_page}: {str(e)}")
                continue
            
        ## Check for next page
        try:
            # Scroll to bottom to ensure pagination is visible
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for any lazy-loaded content
            
            next_url = get_next_page_url(driver)
            if not next_url:
                logger.info("Reached last page or no next page found")
                break
                    
        except WebDriverException as e:
            logger.error(f"WebDriver error on page {current_page}: {str(e)}")
            break
        except Exception as e:
            logger.error(f"Error checking pagination: {str(e)}")
            break

        # finally:
        #     # Close current tab and switch back to parent
        #     time.sleep(random.uniform(2, 5))
    return data

def get_next_page_url(driver: webdriver.Chrome) -> Optional[str]:
    """
    Get the URL of the next page if available.
    
    Args:
        driver: Chrome WebDriver instance
        
    Returns:
        URL of next page or None if no next page
    """
    try:
        logger.info("In get_next_page_url")
        # check if there is only one page
        pages = driver.find_elements(
            By.XPATH, 
            "//div[@class='wt-show-lg']/nav[@aria-label='Pagination of listings']"
            )
        # if len(pages) == 1:
        #     return None
        # get the first page navigation element
        pages = driver.find_elements(
            By.XPATH, 
            "//div[@class='wt-show-lg']/nav[@aria-label='Pagination of listings']/div/div"
            )
        if not pages:
            return None
        # Execute this to move to page
        driver.execute_script(
            "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", 
            pages[-1])
        time.sleep(random.uniform(1, 2))
        # Get next page
        last_elem = pages[-1]
        disabled_links = last_elem.find_elements(By.XPATH, ".//a[contains(@class, 'wt-is-disabled')]")
        
        if not disabled_links:
            next_page_link = last_elem.find_element(By.XPATH, ".//a")
            href = next_page_link.get_attribute("href")
            last_elem.click()
            time.sleep(random.uniform(1, 2))
            return href
        
        return None
        
    except NoSuchElementException:
        logger.info("No pagination found")
        return None
    except StaleElementReferenceException:
        logger.info("Stale element reference exception")
        return None

def detail_scraping(driver: webdriver.Chrome, url: str, store: str) -> Optional[List[Dict[str, str]]]:
    """
    Scrape detailed product information from a product page.
    
    Args:
        driver: Chrome WebDriver instance
        url: Product page URL
        
    Returns:
        List of dictionaries containing product data for each image, or None if error
    """
    try:
        driver.implicitly_wait(WAIT_TIME)
        time.sleep(random.uniform(2, 7))
        
        # Get product name
        try:
            name_element = driver.find_element(
                By.XPATH, 
                "//h1[@class='wt-line-height-tight wt-break-word wt-text-body']"
                )
            name = name_element.text.strip()
        except NoSuchElementException:
            logger.error(f"Could not find product name for URL: {url}")
            return None
        
        # Get tags
        tagnames = get_product_tags(driver)
        random_crawling(driver)
        
        # Get image URLs
        img_urls = get_product_images(driver)
        
        if not img_urls:
            logger.warning(f"No images found for product: {name}")
            return None
        
        # Create data entries for each image
        product_data = []
        for img_url in img_urls[:1]:
            product_data.append({
                "store": store,
                "name": name,
                "tags": tagnames,
                "img_url": img_url,
                "product_url": url
            })
        
        logger.info(f"Successfully scraped product '{name}' with {len(img_urls)} images")
        return product_data
        
    except WebDriverException as e:
        logger.error(f"WebDriver error scraping {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {str(e)}")
        return None

def get_product_tags(driver: webdriver.Chrome) -> str:
    """Get product tags as comma-separated string."""
    try:
        tags = driver.find_elements(
            By.XPATH, 
            "//div[@class='tags-section-container tag-cards-section-container-with-images']/ul/li"
            )
        tag_names = []
        
        for tag in tags:
            try:
                tag_text = tag.find_element(By.XPATH, ".//a/h3").text.strip()
                if tag_text:
                    tag_names.append(tag_text)
            except NoSuchElementException:
                continue
        
        return ",".join(tag_names)
        
    except NoSuchElementException:
        logger.info("No tags found for product")
        return ""

def get_product_images(driver: webdriver.Chrome) -> List[str]:
    """Get list of unique product image URLs."""
    try:
        img_elements = driver.find_elements(
            By.XPATH, 
            "//li[contains(@class, 'wt-position-absolute')]//img"
            )
        img_urls = set()  # Use set to avoid duplicates
        
        for img in img_elements:
            # Get regular src
            # src = img.get_attribute("src")
            # if src and src.startswith("http"):
            #     img_urls.add(src)
            
            # Get zoom src
            zoom_src = img.get_attribute("data-src-zoom-image")
            if zoom_src and zoom_src.startswith("http"):
                img_urls.add(zoom_src)
        
        return list(img_urls)
        
    except Exception as e:
        logger.error(f"Error getting product images: {str(e)}")
        return []

def random_crawling(driver: webdriver.Chrome, is_card: bool = False) -> None:
    """
    Simulate human-like scrolling behavior.
    
    Args:
        driver: Chrome WebDriver instance
    """
    try:
        time.sleep(random.uniform(3, 7))
        # Get page height
        page_height = driver.execute_script("return document.body.scrollHeight")
        if is_card:
            page_height = int(page_height/2)
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Start from top
        current_position = 0
        
        max_iterations = 50  # Prevent infinite loop
        iteration = 0
        if random.random() < 0.2:
            while current_position < page_height and iteration < max_iterations:
                iteration += 1
                # Random scroll amount (between 100 and 300 pixels)
                scroll_amount = random.randint(100, 300)
                
                # Sometimes scroll up a bit (5% chance)
                if random.random() < 0.2 and current_position > viewport_height:
                    scroll_amount = -random.randint(50, 150)
                
                # Calculate new position
                new_position = max(0, min(current_position + scroll_amount, page_height))
                
                # Smooth scroll to new position
                driver.execute_script(f"""
                    window.scrollTo({{
                        top: {new_position},
                        behavior: 'smooth'
                    }});
                """)
                
                # Update current position
                current_position = new_position
                
                # Random pause between scrolls (0.5 to 2 seconds)
                time.sleep(random.uniform(0.5, 2))
                
                # Occasionally pause longer (10% chance)
                if random.random() < 0.1:
                    time.sleep(random.uniform(2, 5))
                
    except Exception as e:
        logger.error(f"Error during random crawling: {str(e)}")

def determined_crawling(driver: webdriver.Chrome) -> None:
    """
    Args:
        driver: Chrome WebDriver instance
    """
    try:
        time.sleep(random.uniform(3, 7))
        # Get page height
        page_height = driver.execute_script("return document.body.scrollHeight")
        # viewport_height = driver.execute_script("return window.innerHeight")
        
        # Start from top
        current_position = 0
        
        max_iterations = 50  # Prevent infinite loop
        iteration = 0
  
        while current_position < page_height and iteration < max_iterations:
            iteration += 1
            # Random scroll amount (between 100 and 300 pixels)
            scroll_amount = 300
            

            # Calculate new position
            new_position = max(0, min(current_position + scroll_amount, page_height))
            
            # Smooth scroll to new position
            driver.execute_script(f"""
                window.scrollTo({{
                    top: {new_position},
                    behavior: 'smooth'
                }});
            """)
            # Update current position
            current_position = new_position
            # Random pause between scrolls (0.5 to 2 seconds)
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error during determined crawling: {str(e)}")


def initiate_drivers() -> List:
    try:
        num_driver = int(os.getenv("NUMDRIVER", "1"))
        active_drivers = list()
        for i in range(1, num_driver + 1):
            profile = int(os.getenv(f"PROFILE_ID_CRAWL_{i}", str(i)))
            driver = open_gemlogin_driver(profile_id=profile)
            if driver:
                active_drivers.append((driver, profile))
        if len(active_drivers) < num_driver or len(active_drivers) == 0:
            return list()
    except AttributeError as e:
        logger.info(f"Error in initiate_drivers {e}")
        return list()
    return active_drivers

def generate_skus(last_skus: str, length: int) -> list:
    data_skus = list()
    next_sku = sku_generator(last_skus)
    for _ in range(length):
        data_skus.append([next_sku])
        cur_sku = next_sku
        next_sku = sku_generator(cur_sku)
    return data_skus

def extract_store_name(str_url: str) -> str:
    str1 = re.search(r"https://www.etsy.com/shop/([A-Za-z0-9]+)\?.*", str_url)
    str2 = re.search(r"https://www.etsy.com/shop/([A-Za-z0-9]+)$", str_url)
    if str1:
        store = str1.group(1)
    elif str2:
        store = str2.group(1)
    else:
        store = "StoreUnknown"
    return store
