from typing import Dict, Any, Union, Generator
from googleapiclient.errors import HttpError
from src.logger import setup_logger


logger = setup_logger(name="GSheetLogger", log_dir="logs")

class GSheetWrite:
    def __init__(self, service):
        self.service = service

    def write_to_gsheet_value(self, spreadsheetId: str, range_name: str, data: Union[str, list]):
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

    def check_last_value_in_column(self, spreadsheetId, range_name) -> int:
        """
        Check the last value in the column
        If not hit the last row, return 2
        If hit the last row, return the next empty row
        """
        try:
            _result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheetId, range=range_name)
                .execute()
                )

            _values = _result.get('values', [])

            last_row_index = -1 # Flag for not hit the last row
            for i in reversed(range(len(_values))):
                if _values[i] and _values[i][0].strip():  # if not empty or just spaces
                    last_row_index = i # Because we start from row i in the sheet
                    break
            if last_row_index == -1: # If not hit the last row
                logger.info(f"No non-empty values found.")
                return 2
            return last_row_index + 1

        except Exception as err:
            logger.error(f'GSheetWrite: An error occurred: {err}')
            return 2
            
class GSheetRead:
    def __init__(self, service):
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
    
    def filter_data_by_column_get_row(self, filter_column: str, filter_value:str, spreadsheetId: str, sheet_name: str) -> Generator[int, None, None]:
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