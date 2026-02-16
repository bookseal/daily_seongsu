import time
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crawler.scraper import SeoulSubwayCollector
from crawler.storage_supabase import SupabaseStorage

load_dotenv()

def run_backfill(start_date="2024-01-01", end_date=None):
    """
    Fetches daily subway data from start_date to end_date (default: yesterday).
    Focuses on ' Seongsu' (handled by Collector filter if configured, otherwise fetches all line 2).
    """
    if end_date is None:
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"=== Starting Backfill: {start_date} ~ {end_date} ===")
    
    try:
        collector = SeoulSubwayCollector()
        storage = SupabaseStorage()
        
        current = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        total_days = (end - current).days + 1
        processed = 0
        
        logs = []
        
        while current <= end:
            target_date = current.strftime("%Y%m%d")
            print(f"[{processed+1}/{total_days}] Fetching {target_date}...")
            
            try:
                data = collector.fetch_daily_passenger_count(target_date)
                if data:
                    _ = storage.save_subway_data(data)
                    msg = f"✅ {target_date}: Saved {len(data)} rows."
                else:
                    msg = f"⚠️ {target_date}: No data from API."
            except Exception as e:
                msg = f"❌ {target_date}: Error - {e}"
                
            print(msg)
            logs.append(msg)
            
            current += timedelta(days=1)
            processed += 1
            time.sleep(0.1) # Rate limit protection
            
        return "\n".join(logs)
    except Exception as e:
        traceback.print_exc()
        return f"CRITICAL ERROR: {str(e)}"

if __name__ == "__main__":
    run_backfill()
