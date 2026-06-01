"""
B4. Bind Live Stream (HLS)

Programmatically request a live HLS stream URL from the Imou cloud.
HLS is compatible with web browsers, VLC, and most players.

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
DEVICE_ID = "YOUR_DEVICE_ID"          # From discovery
BASE_URL = "https://openapi.easy4ip.com/openapi"
PROFILE = "HD"                        # HD or SD
# =================================================


def sign(timestamp, nonce):
    s = f"time:{timestamp},nonce:{nonce},appSecret:{APP_SECRET}"
    return hashlib.md5(s.encode()).hexdigest()


def call(api, payload, token=None):
    ts = round(time.time())
    nonce = secrets.token_urlsafe()
    body = {
        "system": {
            "ver": "1.0",
            "sign": sign(ts, nonce),
            "appId": APP_ID,
            "time": ts,
            "nonce": nonce,
        },
        "params": payload,
        "id": str(random.randint(1, 10000)),
    }
    if token:
        body["params"]["token"] = token

    r = requests.post(f"{BASE_URL}/{api}", json=body, timeout=30)
    r.raise_for_status()
    return r.json().get("result", {})


def get_token():
    return call("accessToken", {}).get("accessToken")


def bind_stream(token):
    stream_id = 0 if PROFILE.upper() == "HD" else 1
    return call(
        "bindDeviceLive",
        {"deviceId": DEVICE_ID, "channelId": "0", "streamId": stream_id},
        token=token,
    )


def get_existing_stream(token):
    return call(
        "getLiveStreamInfo",
        {"deviceId": DEVICE_ID, "channelId": "0"},
        token=token,
    )


def main():
    print("Authenticating...")
    token = get_token()

    print(f"Checking existing stream for {DEVICE_ID}...")
    existing = get_existing_stream(token)
    print(f"Existing: {existing}")

    print(f"Binding new {PROFILE} stream...")
    result = bind_stream(token)
    streams = result.get("streams", [])
    if streams:
        hls = streams[0].get("hls")
        print(f"\nHLS URL: {hls}")
        print("\nPlay commands:")
        print(f"  VLC     : vlc '{hls}'")
        print(f"  ffplay  : ffplay '{hls}'")
        print(f"  Browser : Open directly (if CORS allows)")
    else:
        print("Failed to bind stream")


if __name__ == "__main__":
    main()
