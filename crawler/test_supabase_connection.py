from storage_supabase import SupabaseStorage
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("Testing Supabase Connection...")
    storage = SupabaseStorage()
    
    # Dummy Weather Data
    dummy_data = {
        'response': {
            'body': {
                'items': {
                    'item': [
                        {'category': 'T1H', 'baseDate': '20260101', 'baseTime': '1200', 'obsrValue': '25.5'},
                        {'category': 'PTY', 'baseDate': '20260101', 'baseTime': '1200', 'obsrValue': '0'},
                        {'category': 'REH', 'baseDate': '20260101', 'baseTime': '1200', 'obsrValue': '50'}
                    ]
                }
            }
        }
    }
    
    print("Attempting to insert dummy weather data...")
    try:
        storage.save_weather_data(dummy_data)
        print("[SUCCESS] Dummy data insertion didn't throw an error (Check Supabase Dashboard to confirm row).")
    except Exception as e:
        print(f"[FAILURE] Insertion failed: {e}")

if __name__ == "__main__":
    test_connection()
