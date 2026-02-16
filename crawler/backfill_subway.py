
import os
import time
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crawler.scraper import SeoulSubwayCollector
from crawler.storage_supabase import SupabaseStorage


# Ensure we load .env from the crawler directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)


def run_subway_backfill(start_date="20220101", end_date="20251231"):
    """
    Fetches daily subway data from start_date to end_date.
    Yields logs for real-time Gradio updates.
    """
    if end_date is None:
        # Seoul Data API usually has a 3-day lag. We use 4 days for safety.
        end_date = (datetime.now() - timedelta(days=4)).strftime("%Y%m%d")
    
    yield f"=== Starting Subway Backfill: {start_date} ~ {end_date} ===\n"
    
    # 1. Subway Backfill
    try:
        collector = SeoulSubwayCollector()
        storage = SupabaseStorage()
        
        current = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        total_days = (end - current).days + 1
        processed = 0
        
        yield "🚇 [Subway] Accessing Seoul Data Plaza API...\n"
        
        while current <= end:
            target_date = current.strftime("%Y%m%d")
            status_prefix = f"[Subway {processed+1}/{total_days}] {target_date}: "
            
            try:
                data = collector.fetch_daily_passenger_count(target_date)
                if data:
                    storage.save_subway_data(data)
                    msg = f"✅ Saved {len(data)} rows"
                else:
                    msg = "⚠️ No data"
            except Exception as e:
                msg = f"❌ Error: {str(e)}"
            
            yield f"{status_prefix}{msg}\n"
            
            current += timedelta(days=1)
            processed += 1
            time.sleep(0.1) # Rate limit protection
            
    except Exception as e:
        traceback.print_exc()
        yield f"CRITICAL SUBWAY ERROR: {str(e)}\n"

    yield "=== Subway Backfill Complete ==="

if __name__ == "__main__":
    run_subway_backfill()
