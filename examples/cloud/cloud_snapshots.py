"""
B6. Cloud Snapshots

Request a fresh snapshot image via the Imou cloud API.
The device will wake up if it is in dormant/sleep mode.

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
DEVICE_ID = "YOUR_DEVICE_ID"
BASE_URL = "https://openapi.easy4ip.com/openapi"
OUTPUT_FILE = "cloud_snapshot.jpg"
# =================================================


def api_call(api, payload, token=None):
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


def get_token():
    return api_call("accessToken", {}).get("accessToken")


def request_snapshot(token):
    """Request snapshot via cloud API."""
    print("Requesting snapshot...")
    result = api_call(
        "deviceSnap",
        {"deviceId": DEVICE_ID, "channelId": "0"},
        token=token,
    )
    # The API returns a URL to download the image
    url = result.get("url")
    if not url:
        print(f"No URL in response: {result}")
        return None
    print(f"Snapshot URL: {url}")
    return url


def download_image(url: str):
    """Download the image from the provided URL."""
    print("Downloading image...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(OUTPUT_FILE, "wb") as f:
        f.write(r.content)
    print(f"Saved to {OUTPUT_FILE} ({len(r.content)} bytes)")


def main():
    token = get_token()
    url = request_snapshot(token)
    if url:
        download_image(url)
    else:
        print("Failed to get snapshot")


if __name__ == "__main__":
    main()
