import os
from dotenv import load_dotenv

load_dotenv()


sheet_name_get_link = os.getenv("SHEET_FETCH_URL")
sheet_name_put_data = os.getenv("SHEET_NAME_IMG")
spreadsheetId = os.getenv("SPREADSHEET_ID")

PROFILE_CRE = int(os.getenv("PROFILE_ID_5", "5"))

# SHOP_NAME
# PROFILE_ID
# NUMPAGE
# BASE_URL
# SPREADSHEET_ID
# SHEET_NAME
# SHEET_FETCH_URL
# SHEET_NAME_IMG

# PROFILE_ID_1
# PROFILE_ID_2
# NUMDRIVER

# PROFILE_ID_CRAWL_1
# PROFILE_ID_CRAWL_2

# RESOLUTION_SETTINGS
# NUMIMG
# DESIGN

# PROFILE_ID_5