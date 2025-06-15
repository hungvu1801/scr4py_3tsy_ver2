from dotenv import load_dotenv
from datetime import datetime
import os
import sys
import logging

from src.GSheetWriteRead import GSheetWrite
from src.assets import update_cols_ideogram, update_cols_etsy
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.settings import IDEOGRAM_URL, DATA_DOWNLOAD, LOG_DIR, ETSY_URL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, 'scraper.log')))

def main(search_term: str, start_page: int, end_page: int) -> None:
    """
    Main function to run the scraper.
    
    Args:
        search_term: The search term to look for on Etsy
        start_page: The starting page number
        end_page: The ending page number
    """
    driver = None
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")

    
    gsheet_writer = GSheetWrite(
        update_cols=update_cols_etsy,
        spreadsheetId=spreadsheetId,
        sheet_name=sheet_name,
        queue_number=10)
    
    try:
        driver = open_gemlogin_driver()
        # Create CSV file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        driver.get(IDEOGRAM_URL)

        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        if driver:
            close_gemlogin_driver(driver)
