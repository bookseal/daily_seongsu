import os
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def verify_seoul_data():
    print("\n[1] Testing Seoul Data API Key...")
    api_key = os.getenv("SEOUL_DATA_API_KEY")
    if not api_key or "your_" in api_key:
        print("❌ FAILED: Key is missing or placeholder.")
        return False
        
    # Testing with a simple call: Realtime station arrival for 'Seongsu'
    url = f"http://swopenAPI.seoul.go.kr/api/subway/{api_key}/json/realtimeStationArrival/0/1/성수"
    try:
        response = requests.get(url)
        data = response.json()
        if "available" in data.get("RESULT", {}).get("code", ""): # Check for service unavailable or error codes in result
             print(f"❌ FAILED: API Error - {data}")
             return False
        if "realtimeArrivalList" in data:
            print("✅ SUCCESS: Successfully fetched subway data.")
            return True
        elif "code" in data.get("RESULT", {}) and data["RESULT"]["code"] == "INFO-000":
             print("✅ SUCCESS: Key accepted (No data currently, but auth worked).")
             return True
        else:
            print(f"⚠️ UNCERTAIN: Response received but unexpected format. {str(data)[:100]}...")
            return False # Conservative fail
    except Exception as e:
        print(f"❌ FAILED: Connection error - {e}")
        return False

def verify_kma_data():
    print("\n[2] Testing KMA (Weather) API Key...")
    api_key = os.getenv("KMA_API_KEY")
    if not api_key or "your_" in api_key:
        print("❌ FAILED: Key is missing or placeholder.")
        return False

    # Using Ultra Short Term Forecast endpoint (same as crawler)
    base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    # Using hardcoded params for verification
    params = {
        "serviceKey": api_key,
        "pageNo": 1,
        "numOfRows": 1,
        "dataType": "JSON",
        "base_date": "20240101", # Old date is fine, just checking auth
        "base_time": "1200",
        "nx": 61,
        "ny": 126
    }
    
    try:
        response = requests.get(base_url, params=params)
        # KMA often returns SERVICE_KEY_IS_NOT_REGISTERED_ERROR in XML if failed
        content = response.text
        if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in content:
            print("❌ FAILED: Key is not registered or invalid (KMA Error).")
            return False
        if "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR" in content:
             print("⚠️ WARNING: Key valid but quota exceeded.")
             return True
        if response.status_code == 200:
            print("✅ SUCCESS: Key accepted (Response received).")
            return True
        else:
             print(f"❌ FAILED: Status code {response.status_code}")
             return False
    except Exception as e:
        print(f"❌ FAILED: Connection error - {e}")
        return False

def verify_supabase():
    print("\n[3] Testing Supabase Credentials...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or "your_" in url:
        print("❌ FAILED: SUPABASE_URL is missing or placeholder.")
        return False
    if not key or "your_" in key:
        print("❌ FAILED: SUPABASE_KEY is missing or placeholder.")
        return False
        
    try:
        client = create_client(url, key)
        # Try a simple read (assuming table exists, or just checking auth by listing)
        # Supabase-py doesn't strictly validate on init, need to make a request.
        # We'll try to select from 'weather_data' (limit 1)
        _ = client.table("weather_data").select("*").limit(1).execute()
        print("✅ SUCCESS: Connection established and query executed.")
        return True
    except Exception as e:
        msg = str(e)
        if "JWT" in msg or "Invalid API key" in msg or "401" in msg:
             print("❌ FAILED: Authentication failed (Invalid Key).")
        elif "404" in msg:
             print("⚠️ PARTIAL: Auth worked but table not found (Check schema).")
             return True # Key is likely good, just schema missing
        else:
             print(f"❌ FAILED: {msg}")
        return False

if __name__ == "__main__":
    print("=== API KEY VERIFICATION TOOL ===")
    v1 = verify_seoul_data()
    v2 = verify_kma_data()
    v3 = verify_supabase()
    
    print("\n=== SUMMARY ===")
    print(f"Seoul Subway: {'✅ OK' if v1 else '❌ FAIL'}")
    print(f"KMA Weather : {'✅ OK' if v2 else '❌ FAIL'}")
    print(f"Supabase    : {'✅ OK' if v3 else '❌ FAIL'}")
