import logging
import sys
import random
import time
import csv
from datetime import datetime
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from typing import Generator, Dict, List, Optional

from src.assets import update_cols_etsy
from src.logger import setup_logger
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.GSheetWriteRead import GSheetWrite
from src.settings import ETSY_URL, WAIT_TIME, DATA_DOWNLOAD, LOG_DIR

# from src.utils.gg_utils import check_credentials

os.makedirs(f"{LOG_DIR}/etsy_scraper", exist_ok=True)
logger = setup_logger(name="EtsyScraper", log_dir=f"{LOG_DIR}/etsy_scraper")


def card_scraping(driver: webdriver.Chrome, url: str, numpage: int, store: str) -> Generator[Dict[str, str], None, None]:
    """
    Scrape product cards from multiple pages.
    
    Args:
        driver: Chrome WebDriver instance
        url: Starting URL to scrape
        numpage: Maximum number of pages to scrape
        
    Yields:
        Dict containing product information
    """
    current_page = 0
    current_url = url
    driver.get(current_url)
    # random_crawling(driver, is_card=True)
    time.sleep(random.uniform(2, 5))
    
    
    # Store the parent window handle
    parent_window = driver.current_window_handle
    while current_page < numpage:
        current_page += 1
        
        try:
            driver.implicitly_wait(WAIT_TIME)
            
            logger.info(f"{'>' * 27} Scraping page {current_page}/{numpage} {'<' * 27}")
            
            # Get all items on the page
            items = driver.find_elements(By.XPATH, "//div[contains(@class, 'responsive-listing-grid')]/div")
            logger.info(f"Found {len(items)} items on page {current_page}")
            
            if not items:
                logger.warning(f"No items found on page {current_page}")
                break
        #############################################################################################################
            for i in range(len(items)):
                try:
                    items = driver.find_elements(By.XPATH, "//div[contains(@class, 'responsive-listing-grid')]/div")
                    item_url = items[i].find_element(By.XPATH, ".//a").get_attribute("href")
                    if not item_url:
                        logger.warning(f"No URL found for item {i} on page {current_page}")
                        continue
                    
                    # Scroll to item and click
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", items[i])
                    items[i].click()
                    time.sleep(random.uniform(2, 5))
                    
                    # Switch to new tab

                    chwd = driver.window_handles
                    for window in chwd:
                        if window != parent_window:
                            driver.switch_to.window(window)
                            break
                    
                    logger.info(f"Processing item {i}/{len(items)}: {item_url}")
                    product_datas = detail_scraping(driver=driver, url=item_url, store=store)
                    
                    if product_datas:
                        for product_data in product_datas:
                            yield product_data
                    
                except NoSuchElementException:
                    logger.warning(f"Could not find link for item {i} on page {current_page}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing item {i} on page {current_page}: {str(e)}")
                    continue
                finally:
                    # Close current tab and switch back to parent
                    driver.close()
                    driver.switch_to.window(parent_window)
                    time.sleep(random.uniform(2, 5))
            
            ## Check for next page
            try:
                # Scroll to bottom to ensure pagination is visible
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for any lazy-loaded content
                
                next_url = get_next_page_url(driver)
                if next_url:
                    current_url = next_url
                    # driver.get(current_url)
                    logger.info(f"Moving to next page: {next_url}")
                else:
                    logger.info("Reached last page or no next page found")
                    break
                    
            except Exception as e:
                logger.error(f"Error checking pagination: {str(e)}")
                break
                
        except WebDriverException as e:
            logger.error(f"WebDriver error on page {current_page}: {str(e)}")
            break
        except Exception as e:
            logger.error(f"Unexpected error on page {current_page}: {str(e)}")
            break

def get_next_page_url(driver: webdriver.Chrome) -> Optional[str]:
    """
    Get the URL of the next page if available.
    
    Args:
        driver: Chrome WebDriver instance
        
    Returns:
        URL of next page or None if no next page
    """
    try:
        # check if there is only one page
        pages = driver.find_elements(By.XPATH, "//div[@class='wt-show-lg']/nav[@aria-label='Pagination of listings']")
        if len(pages) == 1:
            return None
        # get the first page navigation element
        pages = driver.find_elements(By.XPATH, "//div[@class='wt-show-lg']/nav[@aria-label='Pagination of listings']/div/div")
        if not pages:
            return None
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", pages[-1])
        time.sleep(random.uniform(1, 2))
        last_elem = pages[-1]
        disabled_links = last_elem.find_elements(By.XPATH, ".//a[contains(@class, 'wt-is-disabled')]")
        
        if not disabled_links:
            next_page_link = last_elem.find_element(By.XPATH, ".//a")
            last_elem.click()
            time.sleep(random.uniform(1, 2))
            return next_page_link.get_attribute("href")
        
        return None
        
    except NoSuchElementException:
        logger.info("No pagination found")
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
            name_element = driver.find_element(By.XPATH, "//h1[@class='wt-line-height-tight wt-break-word wt-text-body']")
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
        tags = driver.find_elements(By.XPATH, "//div[@class='tags-section-container tag-cards-section-container-with-images']/ul/li")
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
        img_elements = driver.find_elements(By.XPATH, "//li[contains(@class, 'wt-position-absolute')]//img")
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
        
        if random.random() < 0.2:
            while current_position < page_height:
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

def initiate_drivers() -> list:
    num_driver = int(os.getenv("NUMDRIVER", "1"))
    active_drivers = list()
    for i in range(1, 4):
        profile = int(os.getenv(f"PROFILE_ID_CRAWL_{i}", str(i)))
        driver = open_gemlogin_driver(profile_id=profile)
        if driver:
            active_drivers.append(driver)
    if len(active_drivers) < num_driver or len(active_drivers) == 0:
        return None
    return active_drivers
