import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SeoulSubwayCollector:
    """
    Collects subway passenger data from Seoul Data Square.
    Target Station: Seongsu (Station Code: 211 - Line 2)
    """
    def __init__(self):
        self.api_key = os.getenv("SEOUL_DATA_API_KEY")
        self.base_url = "http://openapi.seoul.go.kr:8088"
        
    def fetch_realtime_station_arrival(self, station_name="성수"):
        """
        Fetches realtime arrival info. (Less useful for daily aggregate but good for live dashboard)
        """
        if not self.api_key:
            print("Warning: SEOUL_DATA_API_KEY is missing")
            return []
            
        # Example URL logic (simplified, usually requires accurate encoding)
        # http://swopenAPI.seoul.go.kr/api/subway/{KEY}/json/realtimeStationArrival/0/5/{station_name}
        url = f"http://swopenAPI.seoul.go.kr/api/subway/{self.api_key}/json/realtimeStationArrival/0/5/{station_name}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("realtimeArrivalList", [])
        except Exception as e:
            print(f"Error fetching subway data: {e}")
            return []

    def fetch_daily_passenger_count(self, user_date):
        """
        Fetches daily passenger count for a specific date (YYYYMMDD).
        Service: CardSubwayStatsNew
        """
        if not self.api_key:
             print("Warning: SEOUL_DATA_API_KEY is missing")
             return None

        # Format: http://openapi.seoul.go.kr:8088/{KEY}/json/CardSubwayStatsNew/1/1000/{DATE}
        url = f"{self.base_url}/{self.api_key}/json/CardSubwayStatsNew/1/1000/{user_date}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "CardSubwayStatsNew" in data and "row" in data["CardSubwayStatsNew"]:
                rows = data["CardSubwayStatsNew"]["row"]
                # Filter for Seongsu station (Line 2)
                # Note: Station names might be Korean "성수"
                seongsu_data = [row for row in rows if row["SUB_STA_NM"] == "성수" and row["LINE_NUM"] == "2호선"]
                return seongsu_data
            return []
        except Exception as e:
            print(f"Error fetching daily subway stats: {e}")
            return []

class WeatherCollector:
    """
    Collects weather data from KMA (Korea Meteorological Administration).
    Location: Seongsu-dong (Grid approximation: X=61, Y=126 for Seongdong-gu)
    """
    def __init__(self):
        self.api_key = os.getenv("KMA_API_KEY")
        # Base URL for Ultra Short Term Forecast
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        self.nx = 61
        self.ny = 126
        
    def fetch_current_weather(self):
        """
        Fetches current weather (Temperature, Precipitation, etc.)
        """
        if not self.api_key:
            print("Warning: KMA_API_KEY is missing")
            return None
            
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        # API requires base_time in HHMM format, closest past hour
        # Logic to find closest hour (not implemented fully robustly here for brevity, assuming run at reasonable times)
        base_time = (now - pd.Timedelta(hours=1)).strftime("%H00") 

        params = {
            "serviceKey": self.api_key, # Note: Encoding might be an issue with requests param, better to put in URL if special chars exist
            "pageNo": 1,
            "numOfRows": 1000,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": self.nx,
            "ny": self.ny
        }

        # Dealing with double decoding issue common in Korean APIs
        # Often the key provided is already decoded or needs specific handling.
        # Here passing as param dict.
        
        try:
            response = requests.get(self.base_url, params=params)
            # If key error, it might return XML or error msg.
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    # Fallback or error handling for XML response
                    return response.text 
            return None
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

