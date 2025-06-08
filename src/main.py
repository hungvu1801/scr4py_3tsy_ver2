from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.settings import MAIN_URL, WAIT_TIME, DATA_DOWNLOAD, LOG_DIR
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from typing import Generator, Dict, List, Optional
import random
import time
import csv
from datetime import datetime
import os
import pathlib

# os.chdir(pathlib.Path(__file__).parent.resolve()) # change working directory to the parent of the current file


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, 'scraper.log')))

def card_scraping(driver: webdriver.Chrome, url: str, numpage: int) -> Generator[Dict[str, str], None, None]:
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
    random_crawling(driver, is_card=True)
    
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
                    product_data = detail_scraping(driver=driver, url=item_url)
                    
                    if product_data:
                        for item_data in product_data:
                            yield item_data
                    
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
            
            # Check for next page
            try:
                # Scroll to bottom to ensure pagination is visible
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for any lazy-loaded content
                
                next_url = get_next_page_url(driver)
                if next_url:
                    current_url = next_url
                    driver.get(current_url)
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
            return next_page_link.get_attribute("href")
        
        return None
        
    except NoSuchElementException:
        logger.info("No pagination found")
        return None

def detail_scraping(driver: webdriver.Chrome, url: str) -> Optional[List[Dict[str, str]]]:
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
        for img_url in img_urls:
            product_data.append({
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
        
        if random.random() < 0.5:
            while current_position < page_height:
                # Random scroll amount (between 100 and 300 pixels)
                scroll_amount = random.randint(100, 300)
                
                # Sometimes scroll up a bit (20% chance)
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
                    time.sleep(random.uniform(3, 7))
                
    except Exception as e:
        logger.error(f"Error during random crawling: {str(e)}")

def main() -> None:
    """Main function to run the scraper."""
    if len(sys.argv) < 3:
        print("Usage: python main.py <shop_name> <profile_id> [numpage]")
        return
    
    shop_name = sys.argv[1]
    profile_id = sys.argv[2]
    
    # Optional numpage argument
    numpage = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    url = f"{MAIN_URL}/shop/{shop_name}"
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DOWNLOAD, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(DATA_DOWNLOAD, f"{shop_name}_{timestamp}.csv")
    
    logger.info(f"Starting scraper for shop: {shop_name}")
    logger.info(f"Data will be saved to: {csv_filename}")
    
    driver = None
    try:
        driver = open_gemlogin_driver(profile_id)
        scraped_count = 0
        
        # Open CSV file and write header
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'tags', 'img_url', 'product_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Scrape and write data
            for result in card_scraping(driver=driver, url=url, numpage=numpage):
                if result:
                    writer.writerow(result)
                    scraped_count += 1
                    # Print progress every 10 items
                    if scraped_count % 10 == 0:
                        logger.info(f"Scraped {scraped_count} items so far...")
        
        logger.info(f"Scraping completed. Total items scraped: {scraped_count}")
        logger.info(f"Data saved to: {csv_filename}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        if driver:
            try:
                close_gemlogin_driver(profile_id)
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")
