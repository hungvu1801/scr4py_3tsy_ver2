import sys

from src.utils.gg_utils import check_credentials
from src.main import main

if __name__ == "__main__":
    # if len(sys.argv) != 4:
    #     print("Usage: python main.py <search_term> <start_page> <end_page>")
    #     sys.exit(1)
    
    # search_term = sys.argv[1]
    # start_page = int(sys.argv[2])
    # end_page = int(sys.argv[3])
    
    # main(search_term=search_term, start_page=start_page, end_page=end_page)
    check_credentials()