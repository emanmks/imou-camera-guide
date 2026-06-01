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
    # Correct parameters for deviceBaseList (tested 2026-06-01)
    result = api_call(
        "deviceBaseList",
        {"bindId": -1, "limit": 50, "type": "bindAndShare", "needApInfo": True},
        token=token,
    )
    devices = result.get("deviceList", [])

    print(f"Total devices: {len(devices)}\n")
    for d in devices:
        print(f"  Device ID    : {d.get('deviceId')}")
        # channel info is nested under channels[]
        channels = d.get("channels", [])
        ch_names = [c.get("channelName", "") for c in channels]
        print(f"  Name         : {', '.join(ch_names) if ch_names else d.get('deviceId')}")
        print(f"  Channels     : {len(channels)}")
        print()


if __name__ == "__main__":
    main()
