from concurrent.futures import ThreadPoolExecutor
import Thread
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import sys
import re


from src.etsy.service import initiate_drivers, card_scraping
from src.GSheetWriteRead import GSheetWrite, GSheetRead
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.logger import setup_logger
from src.settings import LOG_DIR, DATA_DOWNLOAD
from src.utils import gg_utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/etsy_logs", exist_ok=True)
logger = setup_logger(name="IdeogramLogger", log_dir=f"{LOG_DIR}/etsy_logs")



def controller_thread(driver_pool, global_lock, row) -> None:
    """
    Main function to run the scraper.
    
    Args:
        store: The search term to look for on Etsy
        profile_id: The starting page number
        num: The ending page number
    """
    driver = driver_pool.pop()
    
    sheet_name_get_link = os.getenv("SHEET_FETCH_URL")
    sheet_name_put_data = os.getenv("SHEET_NAME")
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    
    gsheet_writer = GSheetWrite(
        service=service,)
    gsheet_read = GSheetRead(
        service=service,)
    url = gg_utils.get_value_from_row(
        gsheet_read=gsheet_read,
        range_name=f"{sheet_name_get_link}!A{row}", spreadsheetId=spreadsheetId,)
    str1 = re.search(r"https://www.etsy.com/shop/([A-Za-z0-9]+)\?.*", url)
    str2 = re.search(r"https://www.etsy.com/shop/([A-Za-z0-9]+)$", url)
    
    if str1:
        store = str1.group(1)
    elif str2:
        store = str1.group(1)
    else:
        store = "StoreUnknown"

    try:
        # Create CSV file with timestamp
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = card_scraping(
            driver=driver, 
            url=url, 
            store=store)
        with global_lock:
            col_A_lr = gsheet_writer.check_last_value_in_column(
                spreadsheetId=spreadsheetId,
                range_name=f"{sheet_name_put_data}!A2:A")
            
            get_last_sku = gg_utils.get_value_from_row(
                gsheet_read=gsheet_read
                range_name=f"{sheet_name_get_link}!A{col_A_lr - 1}"
            )

            


    except Exception as e:
        logger.error(f"Error in controller thread: {str(e)}")
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
    
    gsheet_read = GSheetRead(
        service=service,)
    
    g_lock = Thread.lock()
    while True:
        try:
            row_generator = gsheet_read.filter_data_by_column_get_row(
                filter_column="B", 
                filter_value="Pending",
                spreadsheetId=spreadsheetId, 
                sheet_name=sheet_name_read)
            
            row_lst = list(row_generator)
            if len(row_lst) == 0:
                logger.info("Empty")
            with ThreadPoolExecutor(max_workers=3) as executor:
                for row in row_lst:
                    executor.submit(controller_thread, drivers_pool, row)
        except Exception as e:
            logger.error(f"Error in controller main {e}")