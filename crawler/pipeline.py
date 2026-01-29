
import pandas as pd
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.storage_supabase import SupabaseStorage
from crawler.backfill_weather import OpenMeteoCollector
from crawler.features import FeatureEngineer

# Ensure .env is loaded
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

class DataPipeline:
    def __init__(self):
        self.storage = SupabaseStorage()
        self.weather_collector = OpenMeteoCollector()
        self.fe = FeatureEngineer()
        
        # State persistence for Gradio steps
        self.df_subway = None
        self.df_weather = None
        self.df_merged_cache = None
        self.df_final_cache = None
        self.version_id = f"v2.0_{datetime.now().strftime('%Y%m%d')}"

    # --- Step 6: Calendar ---
    def step_6_calendar(self):
        """
        Mock generation of calendar features for preview.
        In reality, we generate them during merge, but for UI we show a snippet.
        """
        dates = pd.date_range(start="2024-01-01", periods=5).strftime("%Y-%m-%d").tolist()
        demo_df = pd.DataFrame({"date": dates})
        processed = self.fe.add_calendar_features(demo_df)
        return processed[['date', 'year', 'day_of_week', 'is_weekend', 'is_holiday']]

    # --- Step 7: Merge ---
    def step_7_merge(self):
        """
        Fetches Subway and Weather, Merges them.
        Returns: String status, Dataframe preview
        """
        print("📥 [Step 7] Fetching Data...")
        # 1. Subway
        raw_subway = self.storage.fetch_all_subway_data()
        if not raw_subway:
            return "❌ No subway data found.", pd.DataFrame()
        self.df_subway = pd.DataFrame(raw_subway)
        
        # 2. Weather
        min_date = self.df_subway['date'].min()
        max_date = self.df_subway['date'].max()
        print(f"   Date Range: {min_date} ~ {max_date}")
        
        # Try fetching weather (cached or fresh)
        # For simplicity, we fetch fresh from OpenMeteo for range
        self.df_weather = self.weather_collector.fetch_history(min_date, max_date)
        if self.df_weather.empty:
             return "❌ No weather data found.", pd.DataFrame()

        # 3. Merge
        self.df_subway['date'] = pd.to_datetime(self.df_subway['date'])
        self.df_weather['date'] = pd.to_datetime(self.df_weather['date'])
        
        merged = pd.merge(self.df_subway, self.df_weather, on='date', how='left')
        
        # Drop rows where weather might be missing (inner join effect equivalent)
        # merged = merged.dropna(subset=['avg_temp']) 
        
        self.df_merged_cache = merged
        
        return f"✅ Merged {len(merged)} rows.\nRange: {min_date}~{max_date}", merged.head()

    # --- Step 8: Features ---
    def step_8_features(self):
        """
        Generates Lags (1, 7, 364) and Rolling.
        Requires step_7_merge to have run.
        """
        if self.df_merged_cache is None:
            return "❌ Please run Step 7 first.", pd.DataFrame()
        
        df = self.df_merged_cache.copy()
        
        # 1. Calendar
        df = self.fe.add_calendar_features(df, date_col='date')
        
        # 2. Sort
        df['total_traffic'] = df['boarding_count'] + df['alighting_count']
        df.sort_values(by='date', inplace=True)
        
        # 3. Lags
        df['lag_1d'] = df['total_traffic'].shift(1)
        df['lag_7d'] = df['total_traffic'].shift(7)
        df['lag_364d'] = df['total_traffic'].shift(364) # Yearly Seasonality
        
        # 4. Rolling
        df['rolling_7d_avg'] = df['total_traffic'].shift(1).rolling(window=7).mean()
        
        # 5. Clean
        df_clean = df.dropna().copy()
        dropped = len(df) - len(df_clean)
        
        self.df_final_cache = df_clean
        
        msg = f"✅ Generated Features.\nRows: {len(df_clean)} (Dropped {dropped} NaNs)\nFeatures: Lag-1, Lag-7, Lag-364, Rolling-7"
        return msg, df_clean[['date', 'total_traffic', 'lag_1d', 'lag_7d', 'lag_364d', 'rolling_7d_avg']].tail()

    # --- Step 9: Store ---
    def step_9_store(self):
        """
        Validates and Uploads to Supabase.
        """
        if self.df_final_cache is None:
            return "❌ No feature data. Run Step 8 first."
        
        df = self.df_final_cache.copy()
        
        # 1. Validation
        if (df['total_traffic'] < 0).any():
             return "❌ Validation Failed: Negative Traffic Found."
             
        # 2. Versioning
        df['version_id'] = self.version_id
        
        # 3. Format Date
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        # 4. Upload
        try:
            # Filter columns to match Supabase schema
            target_cols = [
                'date', 'year', 'month', 'day', 'day_of_week', 'is_weekend', 'is_holiday',
                'avg_temp', 'precip_total', 'total_traffic',
                'lag_1d', 'lag_7d', 'lag_364d', 'rolling_7d_avg',
                'version_id'
            ]
            # Intersection to be safe (e.g. if precip_total is missing)
            cols_to_use = [c for c in target_cols if c in df.columns]
            
            self.storage.save_model_features(df[cols_to_use])
            
            # Save Local CSV Log
            log_path = f"logs/level2_execution_log_{datetime.now().strftime('%Y%m%d')}.md"
            self.log_execution(log_path, df)
            
            return f"✅ SUCCESS!\nUpserted {len(df)} rows to Supabase.\nVersion: {self.version_id}\nLog: {log_path}"
        except Exception as e:
            return f"❌ Upload Error: {str(e)}"

    def log_execution(self, filepath, df):
        os.makedirs("logs", exist_ok=True)
        with open(filepath, "w") as f:
            f.write(f"# Level 2 Execution Log\n")
            f.write(f"- **Date**: {datetime.now()}\n")
            f.write(f"- **Version**: {self.version_id}\n")
            f.write(f"- **Rows**: {len(df)}\n")
            f.write(f"## Sample Data\n")
            f.write(df.tail().to_markdown())

    # --- Step 10: Verify ---
    def step_10_verify(self):
        """
        Verify that data is correctly stored in Supabase.
        Queries the 'model_features' table.
        """
        try:
            res = self.storage.client.table("model_features").select("*").limit(5).order("date", desc=True).execute()
            data = res.data
            if not data:
                return "⚠️ Table exists but no data found.", pd.DataFrame()
            
            # Count total
            count_res = self.storage.client.table("model_features").select("*", count="exact").limit(1).execute()
            total_count = count_res.count
            
            msg = f"✅ Final Verification Passed!\nTotal Rows in DB: {total_count}\nVersion: {data[0].get('version_id')}"
            return msg, pd.DataFrame(data)
        except Exception as e:
            return f"❌ Verification Failed: {str(e)}", pd.DataFrame()

if __name__ == "__main__":
    # Test Run
    p = DataPipeline()
    print(p.step_7_merge()[0])
    print(p.step_8_features()[0])
    print(p.step_9_store())
