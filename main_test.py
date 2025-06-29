from tests.testwritegsheet import test_write_gsheet, test_check_last_row, test_read_gsheet
import os
from dotenv import load_dotenv
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

if __name__ == "__main__":
    # test_check_last_row()
    # test_read_gsheet()
    test_write_gsheet()