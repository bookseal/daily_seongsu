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

    # 2. Check if already exists
    resp = requests.get(f"{base_url}/nginx/proxy-hosts", headers=headers)
    hosts = resp.json()
    for h in hosts:
        if "daily-seongsu.bit-habit.com" in h["domain_names"]:
            print("Host already exists. Skipping creation.")
            return

    # 3. Create Proxy Host
    print("Creating Proxy Host daily-seongsu.bit-habit.com -> daily-seongsu-container:7860...")
    payload = {
        "domain_names": ["daily-seongsu.bit-habit.com"],
        "forward_scheme": "http",
        "forward_host": "daily-seongsu-container",
        "forward_port": 7860,
        "access_list_id": 0,
        "certificate_id": "new",
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
        # Create (Requests new cert, might take time)
        resp = requests.post(f"{base_url}/nginx/proxy-hosts", json=payload, headers=headers)
        if resp.status_code == 201:
            print("Successfully Created Proxy Host with SSL!")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"Creation Failed ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"Error during creation: {e}")

if __name__ == "__main__":
    run()
