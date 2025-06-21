from dotenv import load_dotenv
import os
import sys
from googleapiclient.discovery import build
from src.assets import update_cols_ideogram, update_cols_etsy

from src.GSheetWriteRead import GSheetWrite, GSheetRead

from src.ideogram.service import (
    
    browse_site, 
    check_default_settings, 
    generate_image, 
    get_data_to_scrape,
    )

from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.logger import setup_logger
from src.settings import LOG_DIR, IMAGE_DOWNLOAD_SAMPLE
from src.utils import gg_utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.makedirs(f"{LOG_DIR}/ideogram_logs", exist_ok=True)
logger = setup_logger(name="IdeogramLogger", log_dir=f"{LOG_DIR}/ideogram_logs")


def controller() -> None:

    driver_1 = driver_2 = None

    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")
    profile_1 = int(os.getenv("PROFILE_ID_1", "2"))
    profile_2 = int(os.getenv("PROFILE_ID_2", "3"))
    
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)

    # last_row, _ = gg_utils.check_last_value_in_column(
    #     spreadsheetId=spreadsheetId, sheet_name=sheet_name, column_search="I", start_row=1)
    # logger.info(f"Last row in column I: {last_row}")
    
    gsheet_writer = GSheetWrite(
        service=service,)
    
    gsheet_read = GSheetRead(
        service=service,)
    
    row_generator = gsheet_read.filter_data_by_column_get_row(
        filter_column="H", 
        filter_value="Pending", 
        spreadsheetId=spreadsheetId, 
        sheet_name=sheet_name)

    try:
        driver_1 = open_gemlogin_driver(profile_id=profile_1)
        driver_2 = open_gemlogin_driver(profile_id=profile_2)
        # Create CSV file with timestamp
        browse_site(driver_1)
        check_default_settings(driver_1)

        while True:
            try:
                row_num = next(row_generator)
                prompt = gg_utils.get_value_from_row(
                    gsheet_read=gsheet_read,
                    range_name=f"{sheet_name}!I{row_num}", 
                    spreadsheetId=spreadsheetId,)
                logger.info(f"prompt at row {row_num}: {prompt}")

                if not prompt:
                    logger.info(f"Skipping empty prompt at row {row_num}")
                    continue
                sku_name = gg_utils.get_value_from_row(
                    gsheet_read=gsheet_read,
                    range_name=f"{sheet_name}!A{row_num}", spreadsheetId=spreadsheetId,)
                
                if not sku_name:
                    logger.info(f"Skipping empty prompt at row {row_num}")
                    continue

                img_url_sample = gg_utils.get_value_from_row(
                    gsheet_read=gsheet_read,
                    range_name=f"{sheet_name}!E{row_num}", spreadsheetId=spreadsheetId,)

                if img_url_sample:
                    logger.info(img_url_sample)
                    gg_utils.download_media(
                        url=img_url_sample,
                        media_type="img",
                        name=f"{sku_name}.png",
                        directory=IMAGE_DOWNLOAD_SAMPLE,)

                if generate_image(
                    driver_gen=driver_1, 
                    driver_down=driver_2, 
                    prompt=prompt, 
                    sku_name=sku_name):

                    gsheet_writer.write_to_gsheet_value(
                        range_name=f"{sheet_name}!H{row_num}",
                        spreadsheetId=spreadsheetId,
                        data="Done"
                    )

            except StopIteration as e:
                logger.info(f"No more data to scrape : {str(e)}")
                break
            except Exception as e:
                logger.error(f"Error in controller: Error while getting data to scrape: {str(e)}")
                break

    except Exception as e:
        logger.error(f"Error in controller: {str(e)}")
    # finally:
    #     close_gemlogin_driver(profile_id=profile_1)
    #     close_gemlogin_driver(profile_id=profile_2)

