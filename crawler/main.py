import os
from scraper import SeongsuScraper
from storage import DataStorage
from datetime import datetime

# Path where the web app can read the data
# In a real scenario, this might be an S3 bucket or a Database.
# For local dev, we write directly to the web/public/data folder.
WEB_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web/public/data/popups.json")

def crawl_seongsu_popups():
    print(f"[{datetime.now()}] Starting crawl for Seongsu popups...")
    
    scraper = SeongsuScraper()
    storage = DataStorage(WEB_DATA_PATH)
    
    data = scraper.fetch_data()
    storage.save_data(data)
    
    print("Crawling finished.")

if __name__ == "__main__":
    crawl_seongsu_popups()
