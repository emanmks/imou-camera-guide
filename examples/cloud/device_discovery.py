"""
B5. Cloud Device Discovery

List all devices bound to your Imou account via the cloud API.
Shows device IDs, models, online status, and capabilities.

Prerequisites:
    pip install requests
"""

import hashlib
import random
import secrets
import time
import requests

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
BASE_URL = "https://openapi.easy4ip.com/openapi"
# =================================================


def api_call(api: str, payload: dict, token: str = None) -> dict:
    ts = round(time.time())
    nonce = secrets.token_urlsafe()
    sign = hashlib.md5(f"time:{ts},nonce:{nonce},appSecret:{APP_SECRET}".encode()).hexdigest()
    body = {
        "system": {"ver": "1.0", "sign": sign, "appId": APP_ID, "time": ts, "nonce": nonce},
        "params": payload,
        "id": str(random.randint(1, 10000)),
    }
    if token:
        body["params"]["token"] = token
    r = requests.post(f"{BASE_URL}/{api}", json=body, timeout=30)
    r.raise_for_status()
    return r.json().get("result", {})


def main():
    print("Authenticating...")
    token = api_call("accessToken", {}).get("accessToken")

    print("Fetching device list...\n")
    result = api_call("deviceBaseList", {"limit": 100}, token=token)
    devices = result.get("deviceList", [])

    print(f"Total devices: {len(devices)}\n")
    for d in devices:
        print(f"  Device ID    : {d.get('deviceId')}")
        print(f"  Name         : {d.get('name')}")
        print(f"  Model        : {d.get('deviceModel')}")
        print(f"  Status       : {d.get('status')}")
        print(f"  Firmware     : {d.get('version')}")
        print(f"  Channels     : {d.get('channelNum')}")
        print(f"  Capabilities : {d.get('ability')}")
        print()


if __name__ == "__main__":
    main()
