import os
import sys


from src.logger import setup_logger
from src.settings import SOFONTSY_DATA_DIR, LOG_DIR
from src.utils.ItemGenerator import ItemGenerator
from src.utils.utils import prompt_open_file
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from .elems import SofontsyItems

from .service import UploadFile


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(f"{LOG_DIR}/sofontsy_logs", exist_ok=True)
os.makedirs(f"{SOFONTSY_DATA_DIR}", exist_ok=True)

logger = setup_logger(name="SofonsyLog", log_dir=f"{LOG_DIR}/sofontsy_logs")


class Controller:
    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        self.driver = open_gemlogin_driver(profile_id=profile_id)
        if not self.driver:
            logger.error("Failed to open driver.")
            raise
        self.pipeline = UploadFile(driver=self.driver)
        self.df = prompt_open_file()

    def controller(self) -> None:
        """
        This function serves as a placeholder for the controller logic.
        It currently does not perform any operations.
        """
        try:
            if self.df.empty:
                logger.error("DF Empty.. Exiting..")
                return
            item_gen = ItemGenerator(platform="sofontsy", ProcessingItem=SofontsyItems)
            item_gen_yield = item_gen.generator_items(self.df)
            self.pipeline.execute(_type="init")
            try:
                while True:
                    item = next(item_gen_yield)
                    print(f"processing item: {item.ID}")
                    self.pipeline.set_current_item(item)
                    self.pipeline.execute(_type="upload")
                    print(f"Done processing item: {item.ID}")
            except StopIteration:
                logger.info("All items processed successfully.")
            except Exception as e:
                logger.error(f"Error {e}")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected. Exiting gracefully.")
            self.close_controller()

    def close_controller(self):
        if self.driver:
            close_gemlogin_driver(self.driver)
