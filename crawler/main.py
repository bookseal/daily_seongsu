import os
import pandas as pd
from datetime import datetime
from scraper import SeoulSubwayCollector, WeatherCollector
from storage_supabase import SupabaseStorage

# Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "web/public/data")
os.makedirs(DATA_DIR, exist_ok=True)

def collect_data():
    print(f"[{datetime.now()}] Starting data collection for Daily Seongsu...")
    
    # 1. Subway Data
    subway_collector = SeoulSubwayCollector()
    yesterday_date_obj = datetime.now() - pd.Timedelta(days=1)
    yesterday = yesterday_date_obj.strftime("%Y%m%d")
    print(f"Fetching subway stats for {yesterday}...")
    subway_data = subway_collector.fetch_daily_passenger_count(yesterday)
    
    if subway_data:
        # Supabase Save
        supabase_storage = SupabaseStorage()
        supabase_storage.save_subway_data(subway_data)
        
        # Local Backup (Optional, for safety)
        # df_subway = pd.DataFrame(subway_data)
        # subway_path = os.path.join(DATA_DIR, f"subway_{yesterday}.csv")
        # df_subway.to_csv(subway_path, index=False)
    else:
        print("No subway data found or error occurred.")

    # 2. Weather Data (Current)
    weather_collector = WeatherCollector()
    print("Fetching current weather...")
    weather_data = weather_collector.fetch_current_weather()
    
    if weather_data:
        # Supabase Save
        supabase_storage = SupabaseStorage() # Re-init or reuse, straightforward to re-init
        supabase_storage.save_weather_data(weather_data)

        # Local Backup
        # weather_path = os.path.join(DATA_DIR, f"weather_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        # try:
        #      import json
        #      with open(weather_path, 'w', encoding='utf-8') as f:
        #          json.dump(weather_data, f, ensure_ascii=False, indent=4)
        # except:
        #      pass
    else:
        print("No weather data found or error occurred.")

    print("Data collection finished.")

if __name__ == "__main__":
    collect_data()
