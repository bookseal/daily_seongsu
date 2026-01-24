import os
from dotenv import load_dotenv

load_dotenv()

keys = ["SEOUL_DATA_API_KEY", "KMA_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
placeholders = ["your_seoul_api_key_here", "your_kma_api_key_here", "your_supabase_url_here", "your_supabase_anon_key_here"]

print("--- ENV CHECK REPORT ---")
all_valid = True
for key, placeholder in zip(keys, placeholders):
    value = os.getenv(key)
    if not value:
        print(f"[MISSING] {key} is not set.")
        all_valid = False
    elif value == placeholder:
        print(f"[PLACEHOLDER] {key} is still set to default placeholder.")
        all_valid = False
    else:
        # Check length as a basic heuristic
        if len(value) < 10:
             print(f"[WARNING] {key} seems too short ({len(value)} chars).")
        else:
             print(f"[OK] {key} is set and looks valid (length: {len(value)}).")

if all_valid:
    print("\nAll keys appear to be set.")
else:
    print("\nSome keys are missing or improper.")
