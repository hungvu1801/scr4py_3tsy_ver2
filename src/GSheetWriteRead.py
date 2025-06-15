from typing import Dict, List, Any, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.gg_utils import check_credentials
import time
from datetime import datetime

class GSheetWrite:
    def __init__(self,
        update_cols: Dict[str, str],
        spreadsheetId: str,
        sheet_name: str, 
        start_column: str="A",
        queue_number: int=10):
        
        self.spreadsheetId = spreadsheetId
        self.sheet_name = sheet_name
        self.start_column = start_column
        self.credentials = check_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
        self.queue = []
        self.queue_number = queue_number
        self.last_row = self.check_last_value_in_column() # next empty row
        self.update_cols = update_cols # {"A": "column_name"}

    def add_to_queue(self, data: Dict[str, str], range_name:str=None) -> None:
        if not range_name:
            clean_data = self.change_data_to_list(data)
            if clean_data is None:
                raise ValueError(f"Data is missing required columns: {self.update_cols.values()}")
            self.queue.append(clean_data)

            if len(self.queue) >= self.queue_number:
                self.write_to_gsheet_batch()
        else:
            self.write_to_gsheet_value(range_name, data)

    def change_data_to_list(self, data: Dict[str, str]) -> List[str]:
        try:
            sorted_keys = sorted(self.update_cols.keys())
            sorted_values = [self.update_cols[key] for key in sorted_keys]
            clean_data = [data[col] for col in sorted_values]
            return clean_data
        except KeyError:
            raise KeyError(f"Data is missing required columns: {self.update_cols.values()}")

    def write_to_gsheet_batch(self) -> None:
        try:
            if self.start_column not in self.update_cols.keys():
                raise ValueError(f"Start column is not in the update columns: {self.update_cols.keys()}")
            
            dest_range = f"{self.sheet_name}!{self.start_column}{self.last_row}:{self.start_column}{self.last_row + len(self.queue)}"
            copy_data = self.queue.copy()
            # Get the values from the source sheet  
            update_body = {
                "values": copy_data,
            }

            # Make new headers
            self.sheet.values().append(
                spreadsheetId=self.spreadsheetId,
                range=dest_range,
                valueInputOption='USER_ENTERED',
                body=update_body
            ).execute()

            last_row = self.get_last_row(copy_data)
            print(f"Next Last row: {last_row}")
            self.queue.clear()
        except Exception as err:
            print(f"An error occurred: {err}")

    def write_to_gsheet_value(self, range_name: str, data: str | list):
        try:
            if isinstance(data, str):
                values = [[data]] # [[data]]
            elif isinstance(data, list):
                values = data # [["data1", "data2"], ["data3", "data4"]]
            range_name = f"{self.sheet_name}!{range_name}"
           
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheetId,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def check_last_value_in_column(self) -> int:
        """
        Check the last value in the column
        If not hit the last row, return 2
        If hit the last row, return the next empty row
        """
        try:
            _range = f'{self.sheet_name}!{self.start_column}1:{self.start_column}'  # ie. A1:A

            _result = (
                self.sheet
                .values()
                .get(spreadsheetId=self.spreadsheetId, range=_range)
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
            print(f'An error occurred: {err}')
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
        spreadsheetId: str, 
        sheet_name: str, 
        last_row: int,
        read_column: int=2, 
        batch: int=10):
        
        self.spreadsheetId = spreadsheetId
        self.sheet_name = sheet_name
        self.credentials = check_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
        self.read_column = read_column
        self.last_row = last_row
        self.batch = batch

    def read_from_gsheet(self, range_name: str) -> None:
        range_name = f"{self.sheet_name}!{self.read_column}2:{self.read_column}{self.last_row}"
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheetId, range=range_name)
                .execute()
            )
            rows = result.get("values", [])
            print(f"{len(rows)} rows retrieved")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        