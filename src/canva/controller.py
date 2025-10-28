
import os
import sys


from src.logger import setup_logger
from src.settings import LOG_DIR
from src.open_driver import open_gemlogin_driver, close_gemlogin_driver
from .service import CanvaService
from src.utils.load_env import *


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.makedirs(f"{LOG_DIR}/canvas_logs", exist_ok=True)

logger = setup_logger(name="CanvasLog", log_dir=f"{LOG_DIR}/canvas_logs")

class Controller:
    def __init__(self, profile_id: str, project_url: str):
        self.project_url = project_url
        self.profile_id = profile_id
        self.driver = open_gemlogin_driver(profile_id=profile_id)
        if not self.driver:
            logger.error("Failed to open driver.")
            raise
        self.pipeline = CanvaService(driver=self.driver)


    def main(self) -> None:
        """
        This function serves as a placeholder for the controller logic.
        It currently does not perform any operations.
        """
        try:
            try:
                self.pipeline.execute(self.project_url)
            except StopIteration:
                logger.info("All items processed successfully.")
            except Exception as e:
                logger.error(f"Error {e}")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected. Exiting gracefully.")
        finally:
            self.close_controller()

    def close_controller(self):
        if self.driver:
            close_gemlogin_driver(self.driver)
