import os
import requests
from dotenv import load_dotenv
from .storage_supabase import SupabaseStorage

# Ensure we load .env from the crawler directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

def verify_supabase_connection():
    print("\n[3] Testing Supabase Connection...")
    try:
        storage = SupabaseStorage()
        if not storage.client:
            print("❌ FAILED: Client init failed.")
            return False
        
        # Lightweight query to check connection
        # Checking 'weather_data' existance by selecting 1 row
        storage.client.table("weather_data").select("count", count="exact").limit(1).execute()
        print("✅ SUCCESS: Connected to Supabase.")
        return True
    except Exception as e:
        print(f"❌ FAILED: Supabase Error - {e}")
        return False

def verify_seoul_data():
    print("\n[1] Testing Seoul Data API Key...")
    api_key = os.getenv("SEOUL_DATA_API_KEY")
    if not api_key:
        print("❌ FAILED: Key is missing.")
        return False
        
    # Test for "CardSubwayStatsNew" (Daily Stats) which is what we use in main.py
    # Using a known valid date.
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CardSubwayStatsNew/1/5/20231024"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check for service codes
        if "CardSubwayStatsNew" in data:
            print("✅ SUCCESS: Successfully fetched daily subway stats.")
            return True
        elif "RESULT" in data:
             code = data["RESULT"].get("code")
             msg = data["RESULT"].get("message")
             print(f"❌ FAILED: API Error - {code}: {msg}")
             return False
        else:
            print(f"⚠️ UNCERTAIN: Unexpected format. {str(data)[:100]}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Connection error - {e}")
        return False

def verify_kma_data():
    print("\n[2] Testing KMA (Weather) API Key...")
    api_key = os.getenv("KMA_API_KEY")
    if not api_key:
        print("❌ FAILED: Key is missing.")
        return False

    base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "serviceKey": api_key,
        "pageNo": 1,
        "numOfRows": 1,
        "dataType": "JSON",
        "base_date": "20240101", 
        "base_time": "1200",
        "nx": 61,
        "ny": 126
    }
    
    try:
        response = requests.get(base_url, params=params)
        content = response.text
        if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in content:
            print("❌ FAILED: Key is not registered or invalid (KMA Error).")
            return False
        if "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR" in content:
             print("⚠️ WARNING: Key valid but quota exceeded.")
             return True
        if response.status_code == 200:
            # Check if it's actually JSON
            try:
                if isinstance(response.json(), dict):
                    print("✅ SUCCESS: Key accepted.")
                    return True
            except:
                 pass
            
            if "OpenAPI_ServiceResponse" in content:
                # XML error response in 200 OK
                print(f"❌ FAILED: KMA returned XML Error despite 200 OK. likely key decode issue.")
                return False
                
            print(f"✅ SUCCESS: Response received (Status 200).")
            return True
        else:
             print(f"❌ FAILED: Status code {response.status_code}")
             return False
    except Exception as e:
        print(f"❌ FAILED: Connection error - {e}")
        return False

if __name__ == "__main__":
    print("=== DATA API VERIFICATION TOOL (Seoul & KMA & Supabase) ===")
    v1 = verify_seoul_data()
    v2 = verify_kma_data()
    v3 = verify_supabase_connection()
    
    print("\n=== SUMMARY ===")
    print(f"Seoul Subway: {'✅ OK' if v1 else '❌ FAIL'}")
    print(f"KMA Weather : {'✅ OK' if v2 else '❌ FAIL'}")
    print(f"Supabase    : {'✅ OK' if v3 else '❌ FAIL'}")
