import os
import sys


from src.logger import setup_logger
from src.settings import LOG_DIR
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from .service import CanvaService
from src.utils.load_env import *
from src.utils.utils import prompt_open_file, generator_url, url_validator


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(f"{LOG_DIR}/canvas_logs", exist_ok=True)

logger = setup_logger(name="CanvasLog", log_dir=f"{LOG_DIR}/canvas_logs")


class Controller:
    def __init__(self, profile_id: str, project_url: str = None):
        self.project_url = project_url
        self.profile_id = profile_id
        self.driver = open_gemlogin_driver(profile_id=profile_id)
        if not self.driver:
            logger.error("Failed to open driver.")
            raise
        self.pipeline = CanvaService(driver=self.driver)
        self.done_items = set()

    def main(self) -> None:
        """
        This function serves as a placeholder for the controller logic.
        It currently does not perform any operations.
        """
        try:
            df = prompt_open_file()
            if df.empty:
                logger.error("File is empty.")
                return
            url_generator = generator_url(df, url_column=0)
            while True:
                try:
                    self.project_url = next(url_generator)
                    if not url_validator(self.project_url):
                        logger.error(f"Invalid URL: {self.project_url}")
                        continue
                    if self.project_url in self.done_items:
                        logger.info(f"URL already processed: {self.project_url}")
                        continue
                    print(self.project_url)
                    # Execute the main pipeline
                    self.pipeline.execute(self.project_url)
                    self.done_items.append(self.project_url)

                except StopIteration:
                    logger.info("All items processed successfully.")
                    break
                except Exception as e:
                    logger.error(f"Error {e}")
                    continue
            self.close_controller()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected. Exiting gracefully.")

    def close_controller(self):
        if self.driver:
            close_gemlogin_driver(self.driver)
