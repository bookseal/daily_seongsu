
import pandas as pd
import os
from dotenv import load_dotenv
from crawler.storage_supabase import SupabaseStorage

# Ensure we load .env from the crawler directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

def get_data_preview(limit=1000):
    """
    Fetches the most recent subway data for preview.
    Returns a pandas DataFrame.
    """
    try:
        storage = SupabaseStorage()
        if not storage.client:
            return pd.DataFrame({"Error": ["Supabase Disconnected"]})
        
        # Fetch data sorted by date descending
        res = storage.client.table("subway_traffic").select("*").order("date", desc=True).limit(limit).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            # Reorder columns for better readability if needed
            cols = ["date", "station_name", "line_number", "boarding_count", "alighting_count"]
            # Filter cols that exist
            cols = [c for c in cols if c in df.columns]
            return df[cols]
        else:
            return pd.DataFrame({"Status": ["No Data Found"]})
            
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})

def check_readiness_stats():
    """
    Checks if we have enough data for Level 2 (Preprocessing).
    Returns a status string.
    """
    try:
        storage = SupabaseStorage()
        if not storage.client: return "❌ Supabase Disconnected"
        
        # Check Subway Count
        res_sub = storage.client.table("subway_traffic").select("count", count="exact").execute()
        count_sub = res_sub.count

        # Check Weather Count
        res_wea = storage.client.table("weather_data").select("count", count="exact").execute()
        count_wea = res_wea.count

        # Get date range (Subway)
        res_min = storage.client.table("subway_traffic").select("date").order("date", desc=False).limit(1).execute()
        res_max = storage.client.table("subway_traffic").select("date").order("date", desc=True).limit(1).execute()
        
        min_date = res_min.data[0]['date'] if res_min.data else "N/A"
        max_date = res_max.data[0]['date'] if res_max.data else "N/A"
        
        status_msg = f"📊 Subway Rows: {count_sub}\n🌤️ Weather Rows: {count_wea}\n🗓️ Dates: {min_date} ~ {max_date}\n"
        
        # Criteria: At least 30 days of data
        if count_sub > 30 and count_wea > 30:
            status_msg += "\n✅ READY FOR LEVEL 2: Data Preprocessing\n- Status: Sufficient Data (Subway + Weather)"
        else:
            status_msg += f"\n⚠️ NOT READY\n- Need > 30 rows.\n- Subway: {count_sub}, Weather: {count_wea}"
            
        return status_msg
            
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print(check_readiness_stats())
    print("\nData Preview:")
    print(get_data_preview(5))
