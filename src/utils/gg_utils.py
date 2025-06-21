from datetime import datetime
import logging
import os

import time
import requests

from typing import Tuple, Any, List, Dict
from urllib.error import ContentTooShortError

# import urllib.request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.logger import setup_logger
from src.settings import LOG_DIR, SCOPES

logger = setup_logger(name="IdeogramLogger", log_dir=f"{LOG_DIR}/ideogram_logs")

def download_media(
        url:str, 
        directory:str, 
        name:str, 
        media_type:str="img") -> int:
    """
    Parameters:
        name: already has extension included, e.g. "img, .png"
    """
    num_of_tried = 0 # Count number of time the request is sent for each image

    while num_of_tried < 2:
        time.sleep(1)
        try:
            os.makedirs(directory, exist_ok=True)
            path = os.path.join(directory, name)
            if type(url) == str:
                # url = quote(url, safe = ':/')
                logger.info(f"Downloading: url : {url}, directory : {directory}, name : {name}")
                if "&export=download" in url or media_type == "mp4":
                    response = requests.get(url, stream=True)
                    # Save the file
                    if response.status_code == 200:
                        with open(path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        return 0
                    else:
                        logger.info(f"Failed to download image: {url} -- Status code: {response.status_code}")
                        return -1
                else:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(path, 'wb') as f:
                            f.write(response.content)
                        return 0
                    else:
                        logger.info(f"Failed to download image: {url} -- Status code: {response.status_code}")
                        return -1

            else:
                print("url is invalid:", url)
                return -1
        except ContentTooShortError: # exception when image is broken, try send request again
            logger.error(f"{ContentTooShortError} -- Retry Download img = {name}; path = {directory}")
            num_of_tried += 1
        except ValueError: # exception when url is not downloadable
            logger.error(f"url is not valid : {url}")
            print("url is invalid:", url)
            return -1
    if num_of_tried >= 2:
        raise ContentTooShortError


def check_last_value_in_column(
        spreadsheetId, 
        sheet_name:str, 
        column_search:str, 
        start_row:int=1) -> Tuple[int, Any]:
    try:
   
        credentials = check_credentials()
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        _range = f'{sheet_name}!{column_search}{start_row}:{column_search}'  # ie. H2:H

        _result = sheet.values().get(spreadsheetId=spreadsheetId, range=_range).execute()

        _values = _result.get('values', [])

        last_row_index = -1
        for i in reversed(range(len(_values))):
            if _values[i] and _values[i][0].strip():  # if not empty or just spaces
                last_row_index = i # Because we start from row i in the sheet
                break
        if last_row_index == -1:
            logger.info(f"No non-empty values found in column {column_search}.")
            return (-1, None)
        last_row_index += start_row
        
        return (last_row_index, _values[i])
    except Exception as err:
        logger.error(f'An error occurred: {err}')
        return (-1, None)

def check_last_value_in_row(spreadsheetId, sheet, sheet_name:str, row_search:int, start_column:str="A") -> Tuple[str, Any]:
    try:

        _range = f'{sheet_name}!{start_column}{row_search}:ZZ{row_search}'  # ie. A2:ZZ2

        _result = sheet.values().get(spreadsheetId=spreadsheetId, range=_range).execute()

        _values = _result.get('values', [])

        row_values = _values[0]  # The first and only row in the result

        last_col_index = -1
        
        for i in reversed(range(len(row_values))):
            if row_values[i] and row_values[i][0].strip():  # if not empty or just spaces
                last_col_index = i # Because we start from row i in the sheet
                break
        col_letter = get_column_letter(last_col_index + get_column_index(start_column))
        if last_col_index == -1:
            logger.info(f"No non-empty values found in column {row_search}.")
            return ("", None)
        
        return (col_letter, row_values[i])
    
    except Exception as err:
        logger.error(f'An error occurred: {err}')
        return (-1, None)

def check_for_checked_rows(spreadsheetId, sheet, sheet_name:str, column_search:str, start_row:int=2) -> list:
    try:
        # Get all values from column H
        _range = f'{sheet_name}!{column_search}{start_row}:{column_search}'  # ie. H2:H

        _result = sheet.values().get(spreadsheetId=spreadsheetId, range=_range).execute()

        _values = _result.get('values', [])

        checked_rows = []
        for i in range(len(_values)):
            if _values[i] and _values[i][0].strip() == 'TRUE':  # if not empty or just spaces
                checked_rows.append(i + start_row) # Because we start from row i in the sheet
        return checked_rows
    except Exception as err:
        logger.error(f'An error occurred: {err}')
        return -1
    
def check_credentials():
    try:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('ThisNotSecretKeyAtAll/token.json'):
            creds = Credentials.from_authorized_user_file('ThisNotSecretKeyAtAll/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[!] Token refresh failed: {e}")
                    creds = None

            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'ThisNotSecretKeyAtAll/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('ThisNotSecretKeyAtAll/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
    except Exception as e:
        logger.error(f"[!] Error checking credentials: {e}")
        return None

def get_column_letter(index: int) -> str:
    """Convert a 0-based column index to Excel-style column letter(s)."""
    result = ""
    while index >= 0:
        remainder = index % 26
        result = chr(65 + remainder) + result
        index = index // 26 - 1
    return result

def get_column_index(column: str) -> int:
    """Convert Excel-style column letter(s) to 0-based index."""
    result = 0
    for char in column:
        result = result * 26 + (ord(char.upper()) - ord('A') + 1)
    return result - 1

def create_new_sheets_with_template(
        spreadsheetId, 
        sheet, 
        source_sheet_name:str, 
        target_sheet_name:str, 
        row_number:int, 
        start_column:str, 
        last_column:str) -> None:
    try:
        # Get the range from the source sheet
        src_range = f"{source_sheet_name}!{start_column}{row_number}:{last_column}{row_number}"
        # Get the values from the source sheet
        copy_src_range = sheet.values().get(spreadsheetId=spreadsheetId, range=src_range).execute()
        copy_src_values = copy_src_range.get('values', [])
        if not copy_src_values:
            return
        # Get sheet metadata to find if the target sheet exists
        sheet_metadata = sheet.get(spreadsheetId=spreadsheetId).execute()
        sheets = sheet_metadata.get("sheets", [])
        is_sh_exist = False
        for sh in sheets:
            if sh['properties']['title'] == target_sheet_name:
                is_sh_exist = True
                break
        if not is_sh_exist:
            # if the target sheet not exist, create it
            add_sheet_request = {
                "addSheet": {
                    "properties": {
                        "title": target_sheet_name
                    }
                }
            }
            sheet.batchUpdate(
                spreadsheetId=spreadsheetId,
                body={"requests": [add_sheet_request]}
            ).execute()
        else:
            clear_range = f'{target_sheet_name}!A2:ZZ1000000'  # Use a large number for rows
            sheet.values().clear(spreadsheetId=spreadsheetId, range=clear_range).execute()
        dest_range = f"{target_sheet_name}!{start_column}{row_number}:{last_column}{row_number}"
        update_body = {
            "values": copy_src_values,
        }
        print(dest_range)
        print(copy_src_values)
        # Make new headers
        sheet.values().update(
            spreadsheetId=spreadsheetId,
            range=dest_range,
            valueInputOption='USER_ENTERED',
            body=update_body
        ).execute()

        logger.info(f"Row {row_number} copied from {source_sheet_name} to {target_sheet_name}.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def append_data_to_sheet(
    spreadsheetId, 
    sheet, 
    sheet_name:str, 
    data: list, 
    start_column:str="A", 
    start_row:int=2) -> None:
    try:
        # Get the range from the source sheet
        dest_range = f"{sheet_name}!{start_column}{start_row}:{start_column}"
        # Get the values from the source sheet
        update_body = {
            "values": data,
        }
        print(dest_range)
        # Make new headers
        sheet.values().append(
            spreadsheetId=spreadsheetId,
            range=dest_range,
            valueInputOption='USER_ENTERED',
            body=update_body
        ).execute()
        print("Append DONE.")
    except Exception as e:
        print(f"An error occurred: {e}", sheet_name)

def write_to_gsheet(
        data: Dict[str, List[str]], 
        spreadsheetId: str, 
        sheet_name: str) -> None:
    creds = check_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    sheet_name = "Source_News_BlockMedia"

    lr_A_col, value = check_last_value_in_column(
        spreadsheetId=spreadsheetId,
        sheet=sheet, 
        sheet_name=sheet_name, 
        column_search="A", 
        start_row=2)
    
    if lr_A_col == -1:
        start_row = 2
        value = 1
    else:
        start_row = lr_A_col + 1
        value = int(value[0]) + 1
  
    update_id = [[i] for i in range(value, value + len(data["title"]))] # Update ID
    update_titles = [[title] for title in data["title"]] # Update titles
    update_contents = [[content] for content in data["content"]] # Update contents
    update_urls = [[news_url] for news_url in data["news_url"]] # Update URLs
    update_date = [[str(datetime.now())] for _ in range(value, value + len(data["title"]))] # Update date


    update_lst = [update_id, update_titles, update_contents, update_urls, update_date]
    update_cols = ['A', 'B', 'C', 'F', 'M']

    for val, col in zip(update_lst, update_cols):
        update_range = f'{sheet_name}!{col}{start_row}:{col}{start_row + len(data["title"]) - 1}'
        update_body = {'values': val}

        sheet.values().update(
            spreadsheetId=spreadsheetId,
            range=update_range,
            valueInputOption='USER_ENTERED',
            body=update_body
        ).execute()

def get_value_from_row(gsheet_read, range_name, spreadsheetId):
    try:
        result_ = gsheet_read.read_from_gsheet(
            range_name=range_name, 
            spreadsheetId=spreadsheetId)
        if not result_ or "values" not in result_ or not result_["values"]:
            logger.error(f"No values found in the range {range_name}.")
            return None
        return result_["values"][0][0]
    except Exception as e:
        logger.error(f"Error in function get_value_from_row : {e}")
        return None