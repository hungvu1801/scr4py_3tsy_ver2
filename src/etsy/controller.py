from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import sys


from src.etsy.service import initiate_drivers
from src.GSheetWriteRead import GSheetWrite, GSheetRead
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.logger import setup_logger
from src.settings import LOG_DIR, DATA_DOWNLOAD
from src.utils import gg_utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/etsy_logs", exist_ok=True)
logger = setup_logger(name="IdeogramLogger", log_dir=f"{LOG_DIR}/etsy_logs")



def controller_thread(driver_pool, url, global_lock) -> None:
    """
    Main function to run the scraper.
    
    Args:
        store: The search term to look for on Etsy
        profile_id: The starting page number
        num: The ending page number
    """
    driver = driver_pool.pop()
    sheet_name_get_link = os.getenv("SHEET_NAME")
    sheet_name_put_data = os.getenv("SHEET_NAME")
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    
    gsheet_writer = GSheetWrite(
        service=service,)
    
    try:
        # Create CSV file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        if driver:
            driver_pool.append(driver)

def controller_main():
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name_read = os.getenv("SHEET_FETCH_URL")
    sheet_name_write = os.getenv("SHEET_NAME_IMG")
    
    drivers_pool = initiate_drivers()
    if not drivers_pool:
        logger.error("Error controller main : making drivers ")
        return
    
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    gsheet_writer = GSheetWrite(
        service=service,)
    
    gsheet_read = GSheetRead(
        service=service,)
    
    row_generator = gsheet_read.filter_data_by_column_get_row(
        filter_column="B", 
        filter_value="Pending",
        spreadsheetId=spreadsheetId, 
        sheet_name=sheet_name_read)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit()]