import base64
from datetime import datetime
import os
import pandas as pd
import pyautogui as pag
from functools import wraps
import random
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from src.logger import setup_logger
from src.settings import LOG_DIR
import tkinter as tk
import time
from typing import Optional

os.makedirs(f"{LOG_DIR}/utils_logs", exist_ok=True)
logger = setup_logger(name="UtilsLogger", log_dir=f"{LOG_DIR}/utils_logs")

def scroll_to_elem(
        driver: webdriver.Chrome, 
        element: Optional[WebElement] = None, 
        new_position: Optional[int] = None) -> None:
    if element is not None:
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
    else:
        driver.execute_script(f"""
            window.scrollTo(
            {{
                top: {new_position},
                behavior: 'smooth'
            }});
            """)
    return None

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

def scroll_page_down(driver: webdriver.Chrome, height: int = None, SCROLL_PAUSE_TIME: int = 2.5) -> None:

    if not height:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("""
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            """)

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    else:
        driver.execute_script(f"window.scrollTo(0, {height});")

def write_pyautogui(message: str, interval: float = 0.05) -> None:
    # time.sleep(3)
    pag.write(message, interval)
    pag.press("enter")


def write_with_delay(element: WebElement, message: str, interval: float = 0.05) -> None:
    """
    This function use to mimic the write interval like in pyautogui.
    """
    for char in message:
        element.send_keys(char)
        time.sleep(interval)
