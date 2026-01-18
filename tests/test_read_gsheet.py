from src.utils import gg_utils
from googleapiclient.discovery import build
import os
from src.GSheetWriteRead import GSheetRead
from dotenv import load_dotenv

load_dotenv()


def test_read():
    credentials = gg_utils.check_credentials()
    service = build("sheets", "v4", credentials=credentials)

    gsheet_read = GSheetRead(
        service=service,
    )
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")
    print(sheet_name)
    row_search = 48880
    row_generator = gsheet_read.filter_data_by_column_get_row(
        filter_column="H",
        filter_value="Pending",
        spreadsheetId=spreadsheetId,
        sheet_name=sheet_name,
        row_search=row_search,
    )
    row_num = next(row_generator)
    print(f"row_num : {row_num}")


if __name__ == "__main__":
    test_read()
