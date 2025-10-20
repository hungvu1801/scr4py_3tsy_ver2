import os
import sys

from src.logger import setup_logger
from src.settings import CREATIVE_DATA_DIR, LOG_DIR
from src.utils import utils
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from src.utils.load_env import *

from .service import UploadFile


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(f"{LOG_DIR}/cre_fab_logs", exist_ok=True)
os.makedirs(f"{CREATIVE_DATA_DIR}", exist_ok=True)

logger = setup_logger(name="CreativeFabricaLog", log_dir=f"{LOG_DIR}/cre_fab_logs")


def controller(profile_id) -> None:
    """
    This function serves as a placeholder for the controller logic.
    It currently does not perform any operations.
    """
    driver = open_gemlogin_driver(profile_id=profile_id)
    try:
        pipeline = UploadFile(driver=driver)
        if not driver:
            logger.error("Failed to open driver.")
            return

        df = utils.prompt_open_file()
        if df.empty:
            logger.error("DF Empty.. Exiting..")
            return
        item_gen = utils.generator_items(df)
        try:
            while True:
                item = next(item_gen)
                print(f"processing item: {item.ID}")
                pipeline.set_current_item(item)
                pipeline.execute()
                print(f"Done processing item: {item.ID}")
        except StopIteration:
            logger.info("All items processed successfully.")
        except Exception as e:
            logger.error(f"Error {e}")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Exiting gracefully.")
    finally:
        if driver:
            close_gemlogin_driver(driver)