import os
from supabase import create_client, Client
import pandas as pd

class SupabaseStorage:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.client: Client = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
        else:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")

    def save_subway_data(self, data):
        """
        Upserts subway traffic data into 'subway_traffic' table.
        Expects data to be a list of dictionaries or a single dictionary.
        """
        if not self.client:
            print("Supabase client not initialized. Skipping save.")
            return

        if not isinstance(data, list):
            data = [data]

        # Process data to match schema
        # Input format from SeoulSubwayCollector (likely):
        # {'USE_DT': '20231024', 'LINE_NUM': '2호선', 'SUB_STA_NM': '성수', 'RIDE_PASGR_NUM': 100, 'ALIGHT_PASGR_NUM': 200, ...}
        
        formatted_data = []
        for row in data:
            try:
                formatted_row = {
                    "date": f"{row['USE_DT'][:4]}-{row['USE_DT'][4:6]}-{row['USE_DT'][6:]}", # YYYYMMDD -> YYYY-MM-DD
                    "station_name": row["SUB_STA_NM"],
                    "line_number": row["LINE_NUM"],
                    "boarding_count": int(row["RIDE_PASGR_NUM"]),
                    "alighting_count": int(row["ALIGHT_PASGR_NUM"])
                }
                formatted_data.append(formatted_row)
            except KeyError as e:
                print(f"Skipping row due to missing key: {e} in {row}")
                continue

        if not formatted_data:
            return

        try:
            # Upserting based on unique constraint (date, station, line)
            response = self.client.table("subway_traffic").upsert(formatted_data, on_conflict="date, station_name, line_number").execute()
            print(f"Successfully saved {len(formatted_data)} records to Supabase (subway_traffic).")
        except Exception as e:
            print(f"Error saving subway data to Supabase: {e}")

    def save_weather_data(self, data):
        """
        Inserts weather data into 'weather_data' table.
        Expects data to be a dictionary from WeatherCollector.
        """
        if not self.client:
            print("Supabase client not initialized. Skipping save.")
            return

        # WeatherCollector returns complex JSON from KMA API. We need to parse it.
        # However, WeatherCollector.fetch_current_weather might assume raw structure.
        # Let's inspect what main.py currently does. It saves raw JSON.
        # We need to extract: temp, rain_type, humidity.
        # KMA API response structure (roughly): response -> body -> items -> item list
        # Categories: T1H (Temp), PTY (Precipitation Type), REH (Humidity)
        
        try:
            items = data['response']['body']['items']['item']
            
            # Simple extraction
            temp = None
            rain_type = None
            humidity = None
            measured_at = None # We should determine this, or just use now()
            
            # Extract basic obs time from first item if available
            base_date = items[0].get('baseDate')
            base_time = items[0].get('baseTime') # HHMM
            if base_date and base_time:
                # Naive ISO formatting: YYYY-MM-DDTHH:MM:00Z (Assuming KST but storing as compatible string)
                # Ideally convert to UTC for "timestamp with time zone"
                from datetime import datetime
                dt_str = f"{base_date}{base_time}"
                dt_obj = datetime.strptime(dt_str, "%Y%m%d%H%M")
                measured_at = dt_obj.isoformat()

            for item in items:
                category = item.get('category')
                obs_value = item.get('obsrValue')
                
                if category == 'T1H': # Temperature
                    temp = float(obs_value)
                elif category == 'PTY': # Precipitation Type
                    rain_type = int(obs_value)
                elif category == 'REH': # Humidity
                    humidity = float(obs_value)
            
            if measured_at is None:
                 from datetime import datetime
                 measured_at = datetime.utcnow().isoformat()

            payload = {
                "measured_at": measured_at,
                "temperature": temp,
                "precipitation_type": rain_type,
                "humidity": humidity
            }
            
            response = self.client.table("weather_data").insert(payload).execute()
            print(f"Successfully saved weather data to Supabase (weather_data).")
            
        except Exception as e:
            print(f"Error parsing or saving weather data to Supabase: {e}")
    def fetch_all_subway_data(self):
        """
        Fetches all records from 'subway_traffic' table.
        """
        if not self.client:
            print("Supabase client not initialized.")
            return []

        try:
            # Need to paginate if > 1000 rows. Supabase limit defaults to 1000.
            # For now, let's try to fetch a reasonably large limit or implement Loop.
            # OCI free tier might be slow, but let's just fetch 10000 for verified portfolio.
            response = self.client.table("subway_traffic").select("*").range(0, 9999).execute()
            data = response.data
            return data
        except Exception as e:
            print(f"Error fetching all subway data: {e}")
            return []
    def save_model_features(self, df):
        """
        Upserts processed features to 'model_features' table.
        Expects a pandas DataFrame.
        """
        if not self.client:
            print("Supabase client not initialized.")
            return

        print(f"💾 Upserting {len(df)} feature rows to Supabase...")
        
        # Convert DF to list of dicts
        # Handle nan/inf for JSON compliance if needed? Pandas to_dict usually handles it but json.dumps might choke on NaN.
        # Supabase/PostgREST usually prefers null for NaN.
        df_clean = df.where(pd.notnull(df), None)
        records = df_clean.to_dict(orient='records')
        
        # Batch insert to avoid payload limits
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                self.client.table("model_features").upsert(batch, on_conflict="date").execute()
                print(f"   - Saved batch {i} ~ {i+len(batch)}")
            except Exception as e:
                print(f"❌ Error saving batch {i}: {e}")
                if "relation" in str(e) and "does not exist" in str(e):
                    print("⚠️ Table 'model_features' does not exist. Please run the SQL script.")
                    return
