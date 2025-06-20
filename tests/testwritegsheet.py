from src.GSheetWriteRead import GSheetWrite, GSheetRead
from src.assets import update_cols_etsy
from src.utils import gg_utils
from googleapiclient.discovery import build
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def make_random_data(i: int):
    return {
        "name": f"test{i}",
        "tags": f"tag{i}",
        "img_url": f"img{i}",
        "product_url": f"http://example.com/{i}"
    }

def test_write_gsheet():
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    
    if not spreadsheetId or not sheet_name:
        raise ValueError("Environment variables SPREADSHEET_ID and SHEET_NAME must be set")
    
    gsheet_writer = GSheetWrite(
        update_cols=update_cols_etsy,
        spreadsheetId=spreadsheetId,
        sheet_name=sheet_name,
        queue_number=5,
        start_column="A")
    gsheet_writer.write_to_gsheet_value("A25", "test0")

    gsheet_writer.write_to_gsheet_value("A26:A27", [["test"], ["test2"]])
    for i in range(11):
        gsheet_writer.add_to_queue(make_random_data(i))

    gsheet_writer.close_queue()

def test_read_gsheet():
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    
    if not spreadsheetId or not sheet_name:
        raise ValueError("Environment variables SPREADSHEET_ID and SHEET_NAME must be set")
    gsheet_read = GSheetRead(
        spreadsheetId=spreadsheetId,
        sheet_name="Ongoing",
        last_row=77,
        read_column="I")
    print(gsheet_read.read_from_gsheet())

def test_check_last_row():
    spreadsheetId = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME_IMG")
    credentials = gg_utils.check_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    if not spreadsheetId or not sheet_name:
        raise ValueError("Environment variables SPREADSHEET_ID and SHEET_NAME must be set")
    
    last_row, _ = gg_utils.check_last_value_in_column(
        spreadsheetId=spreadsheetId, sheet_name=sheet_name, sheet=sheet, column_search="I", start_row=1)
    print(last_row)
