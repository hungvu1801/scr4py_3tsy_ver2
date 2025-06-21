from typing import Dict, List, Any, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.gg_utils import check_credentials
from src.logger import setup_logger
import time
from datetime import datetime

logger = setup_logger(name="GSheetLogger", log_dir="logs")

class GSheetWrite:
    def __init__(
            self,
            service,):
        self.service = service

        # self.queue = []
        # self.queue_number = queue_number
        # self.last_row = self.check_last_value_in_column() # next empty row
        # self.update_cols = update_cols # {"A": "column_name"}

    # def add_to_queue(self, data: Dict[str, str], range_name:str=None) -> None:
    #     if not range_name:
    #         clean_data = self.change_data_to_list(data)
    #         if clean_data is None:
    #             raise ValueError(f"Data is missing required columns: {self.update_cols.values()}")
    #         self.queue.append(clean_data)

    #         if len(self.queue) >= self.queue_number:
    #             self.write_to_gsheet_batch()
    #     else:
    #         self.write_to_gsheet_value(range_name, data)

    # def change_data_to_list(self, data: Dict[str, str]) -> List[str]:
    #     try:
    #         sorted_keys = sorted(self.update_cols.keys())
    #         sorted_values = [self.update_cols[key] for key in sorted_keys]
    #         clean_data = [data[col] for col in sorted_values]
    #         return clean_data
    #     except KeyError:
    #         raise KeyError(f"Data is missing required columns: {self.update_cols.values()}")

    # def write_to_gsheet_batch(self) -> None:
    #     try:
    #         if self.start_column not in self.update_cols.keys():
    #             raise ValueError(f"Start column is not in the update columns: {self.update_cols.keys()}")
            
    #         dest_range = f"{self.sheet_name}!{self.start_column}{self.last_row}:{self.start_column}{self.last_row + len(self.queue)}"
    #         copy_data = self.queue.copy()
    #         # Get the values from the source sheet  
    #         update_body = {
    #             "values": copy_data,
    #         }

    #         # Make new headers
    #         self.sheet.values().append(
    #             spreadsheetId=self.spreadsheetId,
    #             range=dest_range,
    #             valueInputOption='USER_ENTERED',
    #             body=update_body
    #         ).execute()

    #         last_row = self.get_last_row(copy_data)
    #         logger.info(f"Next Last row: {last_row}")
    #         self.queue.clear()
    #     except Exception as err:
    #         logger.error(f'GSheetWrite: An error occurred: {err}')

    def write_to_gsheet_value(self, spreadsheetId: str, range_name: str, data: str | list):
        try:
            if isinstance(data, str):
                values = [[data]] # [[data]]
            elif isinstance(data, list):
                values = data # [["data1", "data2"], ["data3", "data4"]]
           
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheetId,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            logger.info(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as err:
            logger.error(f'GSheetWrite: An error occurred: {err}')
            return

    def check_last_value_in_column(self, range_name) -> int:
        """
        Check the last value in the column
        If not hit the last row, return 2
        If hit the last row, return the next empty row
        """
        try:
            _result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheetId, range=range_name)
                .execute()
                )

            _values = _result.get('values', [])

            last_row_index = -1 # Flag for not hit the last row
            for i in reversed(range(len(_values))):
                if _values[i] and _values[i][0].strip():  # if not empty or just spaces
                    last_row_index = i # Because we start from row i in the sheet
                    break
            if last_row_index == -1: # If not hit the last row
                print(f"No non-empty values found in column {self.start_column}.")
                return 2
            return last_row_index + 1

        except Exception as err:
            logger.error(f'GSheetWrite: An error occurred: {err}')
            return 2

    def get_last_row(self, queue) -> None:
        self.last_row += len(queue)
        return self.last_row

    def close_queue(self) -> None:
        if self.queue:
            time.sleep(5)
            self.write_to_gsheet_batch()
            
class GSheetRead:
    def __init__(
        self, 
        service):
        self.service = service

    def read_from_gsheet(self, range_name, spreadsheetId) -> Dict[str, Any]:

        try:
            return (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheetId, range=range_name)
                .execute()
            )
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return error
    
    def filter_data_by_column_get_row(self, filter_column: str, filter_value:str, spreadsheetId: str, sheet_name: str) -> List[int]:
        """
        Filter data by column and value
        """
        try:
            range_name = f"{sheet_name}!{filter_column}1:{filter_column}"
            result = self.read_from_gsheet(range_name, spreadsheetId)
            values = result.get('values', [])
            if not values:
                logger.warning("No data found in the sheet")
                return
            for i, row in enumerate(values[1:], start=2):
                if not row or not row[0].strip():
                    logger.warning(f"Row {i} is empty or just spaces. Skipping.")
                    continue
                if row[0] == filter_value:
                    logger.info(f"Found value '{filter_value}' in row {i}.")
                    yield i
            
        except Exception as err:
            logger.error(f'GSheetRead: An error occurred: {err}')
            return