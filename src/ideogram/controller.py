from dotenv import load_dotenv
import os
import sys
from src.assets import update_cols_ideogram, update_cols_etsy

from src.GSheetWriteRead import GSheetWrite, GSheetRead
from src.ideogram.service import (
    browse_site, 
    check_default_settings, 
    generate_image, 
    get_data_to_scrape)
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.logger import setup_logger
from src.settings import LOG_DIR
from src.utils import gg_utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/ideogram_logs", exist_ok=True)
logger = setup_logger(name="IdeogramLogger", log_dir=f"{LOG_DIR}/ideogram_logs")


def controller() -> None:

    driver = None
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")

    last_row, _ = gg_utils.check_last_value_in_column(
        spreadsheetId=spreadsheetId, sheet_name=sheet_name, column_search="I", start_row=1)
    logger.info(f"Last row in column I: {last_row}")
    
    # gsheet_writer = GSheetWrite(
    #     update_cols=update_cols_etsy,
    #     spreadsheetId=spreadsheetId,
    #     sheet_name=sheet_name,
    #     queue_number=10)
    gsheet_reader_I_col = GSheetRead(
        spreadsheetId=spreadsheetId,
        sheet_name=sheet_name,
        last_row=last_row,
        read_column="I")
    
    gsheet_reader_A_col = GSheetRead(
        spreadsheetId=spreadsheetId,
        sheet_name=sheet_name,
        last_row=last_row,
        read_column="A")

    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        driver = open_gemlogin_driver(profile_id=2)
        # Create CSV file with timestamp
        browse_site(driver)
        check_default_settings(driver)
        data_I_col = gsheet_reader_I_col.read_from_gsheet()
        data_A_col = gsheet_reader_A_col.read_from_gsheet()
        prompt_generator = get_data_to_scrape(data_I_col)
        sku_generator = get_data_to_scrape(data_A_col)
        while True:
            try:
                idx_I, val_I = next(prompt_generator)
                if val_I:
                    prompt = val_I[0] # Get prompt from column I
                    logger.info(prompt)
                else:
                    logger.info(f"Skipping empty prompt at row {idx_I}")
                    continue

                _, val_A = next(sku_generator)
                if val_A:
                    sku_name = val_A[0] # Get SKU name from column A
                    logger.info(sku_name)
                else:
                    logger.info(f"Skipping empty SKU name at row {idx_I}")
                    continue
                generate_image(driver, prompt, sku_name)

            except StopIteration as e:
                logger.info(f"No more data to scrape : {str(e)}")
                break
            except Exception as e:
                logger.error(f"Error while getting data to scrape: {str(e)}")
                break

    except Exception as e:
        logger.error(f"Error in controller: {str(e)}")
    finally:
        if driver:
            close_gemlogin_driver(driver)
