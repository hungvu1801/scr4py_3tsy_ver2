import logging

import requests
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def open_gemlogin_driver(profile_id: str) -> webdriver.Chrome:
    BASE_URL = os.getenv("BASE_URL", "http://host.docker.internal:1010")
    response = requests.get(f"{BASE_URL}/api/profiles/start/{profile_id}", timeout=10)
    response.raise_for_status()

    if response.status_code != 200:
        return None
    
    response_json = response.json()
    data = response_json.get('data')
    ## Get resource from response
    driver_path = data.get('driver_path')
    remote_address = data.get('remote_debugging_address')
    
    if not remote_address:
    # chrome_options is already initialized on line 96, redundant initialization removed.
        return None

    chrome_options = Options()
    chrome_service = Service(
        executable_path=driver_path,
    )

    # Uncomment the following line to override the user agent for debugging or testing purposes.
    # driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(USER_AGENTS)})
    
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.debugger_address = remote_address
    
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    # driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": random.choice(USER_AGENTS)})
    return driver

def close_gemlogin_driver(profile_id) -> bool:
    BASE_URL = os.getenv("BASE_URL", "http://host.docker.internal:1010")
    response = requests.get(f"{BASE_URL}/api/profiles/close/{profile_id}", timeout=10)
    return response.status_code == 200
