import requests
import json
import time

base_url = "http://localhost:81/api"
email = "gichanlee@icloud.com"
pw = "!Qudrnng20500"

def run():
    # 1. Login
    print("Trying to login...")
    try:
        resp = requests.post(f"{base_url}/tokens", json={"identity": email, "secret": pw})
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        return

    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login Successful!")

    # 2. Find Host ID
    resp = requests.get(f"{base_url}/nginx/proxy-hosts", headers=headers)
    hosts = resp.json()
    target_id = None
    existing_ssl = False

    for h in hosts:
        if "daily-seongsu.bit-habit.com" in h["domain_names"]:
            target_id = h["id"]
            existing_ssl = h["ssl_forced"]
            break
    
    if not target_id:
        print("Host not found! Please create it first.")
        return

    print(f"Found Host ID: {target_id}")

    # 3. Update with SSL
    # If standard update fails, try deleting and recreating.
    # But let's try update first.
    
    print("Enabling SSL (Requesting Let's Encrypt)... This may take 30+ seconds.")
    
    payload = {
        "domain_names": ["daily-seongsu.bit-habit.com"],
        "forward_scheme": "http",
        "forward_host": "daily-seongsu-container",
        "forward_port": 7860,
        "access_list_id": 0,
        "certificate_id": "new",  # Request new cert
        "ssl_forced": True,
        "meta": {
            "letsencrypt_email": email,
            "letsencrypt_agree": True,
            "dns_challenge": False
        },
        "advanced_config": "",
        "locations": [],
        "block_exploits": True,
        "caching_enabled": False,
        "allow_websocket_upgrade": True,
        "http2_support": False
    }

    try:
        print(f"Updating Host {target_id}...")
        resp = requests.put(f"{base_url}/nginx/proxy-hosts/{target_id}", json=payload, headers=headers)
        
        if resp.status_code in [200, 201]:
            print("Successfully Enabled SSL!")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"Update Failed ({resp.status_code}): {resp.text}")
            # If update fails (500), try create new?
            # Or print error detail.
    except Exception as e:
        print(f"Error during update: {e}")

if __name__ == "__main__":
    run()
