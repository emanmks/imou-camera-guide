"""
B1. Official HTTP API (Raw)

Make raw HTTP calls to Imou Open Platform API.
Demonstrates: access token auth, device discovery, live stream binding.

Prerequisites:
    - AppId and AppSecret from https://open.imoulife.com/consoleNew/myApp/appInfo
    - Region endpoint (see below)

API Docs: https://open.imoulife.com/book/en/http/develop.html
"""

import hashlib
import json
import random
import secrets
import time
import requests

# ================= CONFIGURATION =================
APP_ID = "lc9831fd11e8b54fa8"
APP_SECRET = "7122dd4aac8942b7977a3accd4277b"

# Region endpoints (choose based on your account region):
# Singapore:  https://openapi.easy4ip.com/openapi
# Frankfurt:  https://openapi-fra.easy4ip.com/openapi
# Oregon:     https://openapi-or.easy4ip.com/openapi
# China:      https://openapi.easy4ip.com/openapi
BASE_URL = "https://openapi.easy4ip.com/openapi"
# =================================================


def make_sign(timestamp: int, nonce: str, app_secret: str) -> str:
    """Generate MD5 sign as per Imou API spec."""
    sign_str = f"time:{timestamp},nonce:{nonce},appSecret:{app_secret}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


def api_call(api: str, payload: dict, token: str = None) -> dict:
    """Make a signed POST request to the Imou API."""
    timestamp = round(time.time())
    nonce = secrets.token_urlsafe()
    sign = make_sign(timestamp, nonce, APP_SECRET)
    request_id = str(random.randint(1, 10000))

    body = {
        "system": {
            "ver": "1.0",
            "sign": sign,
            "appId": APP_ID,
            "time": timestamp,
            "nonce": nonce,
        },
        "params": payload,
        "id": request_id,
    }

    if token:
        body["params"]["token"] = token

    url = f"{BASE_URL}/{api}"
    resp = requests.post(url, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Imou wraps responses in a result object, and data is inside result.data
    if "result" in data and "data" in data["result"]:
        return data["result"]["data"]
    if "result" in data:
        return data["result"]
    return data


def get_access_token() -> str:
    """Authenticate and get access token."""
    print("Getting access token...")
    result = api_call("accessToken", {})
    token = result.get("accessToken")
    expire = result.get("expireTime")
    print(f"Access token obtained (expires in {expire}s)")
    return token


def list_devices(token: str):
    """List all devices bound to the account."""
    print("\nListing devices...")
    result = api_call(
        "deviceBaseList",
        {"bindId": -1, "limit": 50, "type": "bindAndShare", "needApInfo": True},
        token=token,
    )
    devices = result.get("deviceList", [])
    print(f"Found {len(devices)} device(s)\n")
    for dev in devices:
        print(f"  Device ID : {dev.get('deviceId')}")
        print(f"  Name      : {dev.get('name')}")
        print(f"  Model     : {dev.get('deviceModel')}")
        print(f"  Online    : {dev.get('status')}")
        print(f"  Channel   : {dev.get('channelNum')}")
        print()
    return devices


def bind_live_stream(token: str, device_id: str, profile: str = "HD"):
    """Bind a live stream to get HLS URL."""
    print(f"\nBinding live stream for {device_id} ({profile})...")
    stream_id = 0 if profile.upper() == "HD" else 1
    result = api_call(
        "bindDeviceLive",
        {"deviceId": device_id, "channelId": "0", "streamId": stream_id},
        token=token,
    )
    # Response contains HLS URL under streams[0].hls
    streams = result.get("streams", [])
    if streams:
        hls_url = streams[0].get("hls")
        live_token = result.get("liveToken")
        print(f"HLS URL   : {hls_url}")
        print(f"Live Token: {live_token}")
        return hls_url
    print("No stream URL returned")
    return None


def main():
    token = get_access_token()
    devices = list_devices(token)

    if not devices:
        print("No devices found. Ensure your camera is bound to the Imou account.")
        return

    # Bind live stream for first device
    first = devices[0]
    hls = bind_live_stream(token, first["deviceId"], profile="HD")

    if hls:
        print(f"\nYou can now play the HLS URL in VLC, browser, or ffmpeg:")
        print(f"  ffplay '{hls}'")


if __name__ == "__main__":
    main()
