from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import sys
import re
from threading import Lock
import time

from src.etsy.service import initiate_drivers, card_scraping, generate_skus, extract_store_name
from src.GSheetWriteRead import GSheetWrite, GSheetRead
from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils import gg_utils, utils


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/etsy_logs", exist_ok=True)
logger = setup_logger(name="EtsyScraper", log_dir=f"{LOG_DIR}/etsy_logs")


def controller_thread(driver_pool: list, global_lock: Lock, row: str) -> None:
    """
    Main function to run the scraper.
    
    Args:
        driver_pool: The search term to look for on Etsy
        global_lock: The starting page number
        row: The ending page number
    """
    logger.info("In controller_thread")
    with global_lock:
        driver = driver_pool.pop() if driver_pool else None
    if not driver:
        logger.error("Empty driver pool.")
        return
    sheet_name_get_link = os.getenv("SHEET_FETCH_URL")
    sheet_name_put_data = os.getenv("SHEET_NAME_IMG")
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    
    gsheet_writer = GSheetWrite(
        service=service,)
    gsheet_read = GSheetRead(
        service=service,)
    url = gg_utils.get_value_from_row(
        gsheet_read=gsheet_read,
        range_name=f"{sheet_name_get_link}!A{row}", 
        spreadsheetId=spreadsheetId,)
    
    store = extract_store_name(url)
    logger.info(f"Extracted store: {store}")

    try:
        # Create CSV file with timestamp
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = card_scraping(
            driver=driver, 
            url=url, 
            store=store)
        if len(data["img_url"]):
            with global_lock:
                logger.info(f"Data found. Writing data to sheet")
                # Get last column
                col_A_lr = gsheet_writer.check_last_value_in_column(
                    spreadsheetId=spreadsheetId,
                    range_name=f"{sheet_name_put_data}!A2:A")
                
                # Get last sku in column A
                last_sku_value = gg_utils.get_value_from_row(
                    gsheet_read=gsheet_read,
                    range_name=f"{sheet_name_put_data}!A{col_A_lr - 1}",
                    spreadsheetId=spreadsheetId
                )
                logger.info(f"Last SKUs: {last_sku_value}")
                # Generate skus
                data_skus = generate_skus(last_skus=last_sku_value, length=len(data["img_url"]))
                data_urls = utils.data_construct_for_gsheet(
                    data=data["img_url"])
                data_store = utils.data_construct_for_gsheet(
                    data=store, length=len(data["img_url"]))
                data_status = utils.data_construct_for_gsheet(
                    data="Pending", length=len(data["img_url"]))
                # Write to column A: SKUs
                gsheet_writer.write_to_gsheet_value(
                    spreadsheetId=spreadsheetId, 
                    range_name=f"{sheet_name_put_data}!A{col_A_lr}", 
                    data=data_skus)
                # Write to column B: Store Name
                gsheet_writer.write_to_gsheet_value(
                    spreadsheetId=spreadsheetId, 
                    range_name=f"{sheet_name_put_data}!B{col_A_lr}", 
                    data=data_store)
                # Write to column E: img_url
                gsheet_writer.write_to_gsheet_value(
                    spreadsheetId=spreadsheetId, 
                    range_name=f"{sheet_name_put_data}!E{col_A_lr}", 
                    data=data_urls)
                # Write to column G: img_url
                gsheet_writer.write_to_gsheet_value(
                    spreadsheetId=spreadsheetId, 
                    range_name=f"{sheet_name_put_data}!G{col_A_lr}", 
                    data=data_status)
                time.sleep(5)
            # Update status in 
            gsheet_writer.write_to_gsheet_value(
                spreadsheetId=spreadsheetId, 
                range_name=f"{sheet_name_get_link}!B{row}",
                data="Done")
                # Wait for data to fully updated
        logger.info(f"Data written to sheet.")
    except Exception as e:
        logger.error(f"Error in controller thread: {str(e)}")
    finally:
        if driver:
            with global_lock:
                driver_pool.append(driver)

def controller_main() -> None:
    num_driver = int(os.getenv("NUMDRIVER", "1"))
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name_read = os.getenv("SHEET_FETCH_URL")
    # sheet_name_write = os.getenv("SHEET_NAME_IMG")
    
    drivers_pool = initiate_drivers()
    if not drivers_pool:
        logger.error("Error controller main : making drivers ")
        return
    
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    
    gsheet_read = GSheetRead(
        service=service,)
    
    global_lock = Lock()
    while True:
        try:
            row_generator = gsheet_read.filter_data_by_column_get_row(
                filter_column="B", 
                filter_value="Pending",
                spreadsheetId=spreadsheetId, 
                sheet_name=sheet_name_read)
            
            row_lst = list(row_generator)
            logger.info(f"Rows to process: {row_lst}")
            if len(row_lst) == 0:
                logger.info("Empty")
            with ThreadPoolExecutor(max_workers=num_driver) as executor:
                for row in row_lst:
                    executor.submit(controller_thread, drivers_pool, global_lock, row)
        except Exception as e:
            logger.error(f"Error in controller main {e}")