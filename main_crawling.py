import sys
from src.main_crawling import main_crawling
from dotenv import load_dotenv
load_dotenv()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py <store> <start_page> <end_page>")
        sys.exit(1)
    
    store = sys.argv[1]
    profile_id = int(sys.argv[2])
    num_page = int(sys.argv[3])
    
    main_crawling(store=store, profile_id=profile_id, num_page=num_page)