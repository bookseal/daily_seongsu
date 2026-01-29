
import requests
import pandas as pd
from datetime import datetime
import time
import os
import sys

# Ensure imports work if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.storage_supabase import SupabaseStorage

class OpenMeteoCollector:
    def __init__(self):
        # Seongsu Station Coordinates
        self.lat = 37.5445
        self.lon = 127.0565
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        self.storage = SupabaseStorage()

    def fetch_history(self, start_date="2022-01-01", end_date="2025-12-31"):
        """
        Fetches daily weather history from Open-Meteo.
        Params:
            start_date (str): YYYY-MM-DD
            end_date (str): YYYY-MM-DD
        """
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum", "rain_sum", "snowfall_sum"],
            "timezone": "Asia/Seoul"
        }
        
        print(f"🌦️ Fetching Weather from Open-Meteo: {start_date} ~ {end_date}...")
        
        try:
            resp = requests.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            daily = data.get("daily", {})
            if not daily:
                print("❌ No daily data found.")
                return pd.DataFrame()
            
            df = pd.DataFrame(daily)
            
            # Formatting
            df.rename(columns={
                "time": "date",
                "temperature_2m_mean": "avg_temp",
                "precipitation_sum": "precip_total",
            }, inplace=True)
            
            # Map rain_sum/snowfall_sum to precipitation_type (simplified)
            # PTY: 0=None, 1=Rain, 2=Rain/Snow, 3=Snow
            def determine_pty(row):
                if row['snowfall_sum'] > 0: return 3 # Snow
                if row['rain_sum'] > 0: return 1 # Rain
                return 0 # None
            
            df['precipitation_type'] = df.apply(determine_pty, axis=1)
            
            print(f"✅ Fetched {len(df)} days of weather data.")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching weather: {e}")
            return pd.DataFrame()

    def save_to_supabase(self, df):
        if df.empty: return False
        
        print(f"💾 Saving {len(df)} weather rows to Supabase...")
        records = []
        for _, row in df.iterrows():
            # Match schema of 'weather_data' table
            # measured_at, temperature, precipitation_type, humidity (missing from OpenMeteo daily, assume 0 or fetch generic)
            # Use 12:00:00 for daily data
            records.append({
                "measured_at": f"{row['date']}T12:00:00", 
                "temperature": row['avg_temp'],
                "precipitation_type": int(row['precipitation_type']),
                "humidity": 0 
            })
            
        try:
             # Batch upsert
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                 batch = records[i:i+batch_size]
                 self.storage.client.table("weather_data").insert(batch).execute()
                 print(f"   - Inserted batch {i}")
            return True
        except Exception as e:
            print(f"❌ Error saving weather: {e}")
            return False

def run_weather_backfill(start_date="20220101", end_date="20251231"):
    """
    Generator for fetching weather data and yielding logs for Gradio.
    """
    yield f"=== Starting Weather Backfill: {start_date} ~ {end_date} ===\n"

    try:
        # Format dates for OpenMeteo (YYYY-MM-DD)
        s_date_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        e_date_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        yield f"🌤️ Connecting to Open-Meteo ({s_date_fmt} ~ {e_date_fmt})...\n"
        
        w_collector = OpenMeteoCollector()
        df_weather = w_collector.fetch_history(s_date_fmt, e_date_fmt)
        
        if not df_weather.empty:
            yield f"✅ Fetched {len(df_weather)} days of weather data.\n"
            
            yield "💾 Saving to Supabase...\n"
            success = w_collector.save_to_supabase(df_weather)
            
            if success:
                yield f"✅ Successfully saved {len(df_weather)} rows to 'weather_data' table.\n"
            else:
                yield f"❌ Failed to save weather data to DB.\n"
        else:
             yield f"⚠️ No weather data found for this period.\n"
             
    except Exception as e:
        yield f"CRITICAL WEATHER ERROR: {str(e)}\n"

    yield "=== Weather Backfill Complete ==="

if __name__ == "__main__":
    collector = OpenMeteoCollector()
    df = collector.fetch_history(start_date="2024-01-01", end_date="2024-01-05")
    collector.save_to_supabase(df)
