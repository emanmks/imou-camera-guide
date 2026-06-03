"""
B4. Bind Live Stream (HLS)

Request a live HLS stream URL from the Imou cloud.
Uses the same two-step flow as the official pyimouapi SDK:
  1. Try getLiveStreamInfo (existing stream)
  2. If LV1002, call bindDeviceLive
  3. If LV1001 after bind, retry getLiveStreamInfo

Prerequisites:
    pip install requests
"""

import hashlib
import logging
import random
import secrets
import time
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
DEVICE_ID = "YOUR_DEVICE_ID"
CHANNEL_ID = "0"
# Initial API URL (netloc only, as SDK does)
INITIAL_API_URL = "openapi.easy4ip.com"
PROFILE = "HD"  # HD → streamId=0, SD → streamId=1
# =================================================


class ImouAPIClient:
    """Minimal sync client matching SDK patterns."""

    def __init__(self, app_id, app_secret, api_url):
        self._app_id = app_id
        self._app_secret = app_secret
        self._api_url = api_url
        self._token = None

    def _sign(self, timestamp, nonce):
        raw = f"time:{timestamp},nonce:{nonce},appSecret:{self._app_secret}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _request(self, endpoint, params=None):
        payload = dict(params) if params else {}
        if self._token is not None and endpoint != "/openapi/accessToken":
            payload["token"] = self._token

        ts = round(time.time())
        nonce = secrets.token_urlsafe()
        body = {
            "system": {
                "ver": "1.0",
                "sign": self._sign(ts, nonce),
                "appId": self._app_id,
                "time": ts,
                "nonce": nonce,
            },
            "params": payload,
            "id": str(random.randint(1, 100000)),
        }

        url = f"https://{self._api_url}{endpoint}"
        r = requests.post(url, json=body, timeout=30)
        r.raise_for_status()
        resp = r.json()
        result = resp.get("result", {})
        code = result.get("code", "")
        msg = result.get("msg", "")
        data = result.get("data", {})

        if code != "0":
            if code == "TK1002":
                _LOGGER.info("Token expired, refreshing...")
                self._token = None
                return self._request(endpoint, params)
            if code in ("LV1002", "LV1001"):
                _LOGGER.warning("Stream status [%s]: %s", code, msg)
                return {}
            raise ValueError(f"[{code}] {msg}")
        return data

    def authenticate(self):
        data = self._request("/openapi/accessToken", {})
        self._token = data.get("accessToken")
        if "currentDomain" in data:
            raw = data["currentDomain"]
            if "://" not in raw:
                raw = f"https://{raw}"
            parsed = urlparse(raw)
            if parsed.netloc:
                _LOGGER.info("Redirect to %s", parsed.netloc)
                self._api_url = parsed.netloc
        expire = data.get("expireTime", "?")
        _LOGGER.info("Token obtained (expires in %ss, API: %s)", expire, self._api_url)
        return self._token

    def get_existing_stream(self, device_id, channel_id):
        return self._request("/openapi/getLiveStreamInfo", {
            "deviceId": device_id,
            "channelId": channel_id,
        })

    def bind_stream(self, device_id, channel_id, stream_id):
        return self._request("/openapi/bindDeviceLive", {
            "deviceId": device_id,
            "channelId": channel_id,
            "streamId": stream_id,
        })


def get_hls_url(data, preferred=0):
    streams = data.get("streams", [])
    if not streams:
        return None
    for s in streams:
        if s.get("streamId") == preferred:
            return s.get("hls")
    return streams[0].get("hls")


def main():
    client = ImouAPIClient(APP_ID, APP_SECRET, INITIAL_API_URL)
    client.authenticate()

    stream_id = 0 if PROFILE.upper() == "HD" else 1

    # Step 1: try existing stream
    _LOGGER.info("Checking existing stream for %s...", DEVICE_ID)
    data = client.get_existing_stream(DEVICE_ID, CHANNEL_ID)
    hls = get_hls_url(data, stream_id)

    if not hls:
        # Step 2: bind new stream
        _LOGGER.info("No existing stream, binding %s...", PROFILE)
        data = client.bind_stream(DEVICE_ID, CHANNEL_ID, stream_id)
        hls = get_hls_url(data, stream_id)

        if not hls and data:
            # LV1001 → retry query
            _LOGGER.info("Stream already exists, querying again...")
            data = client.get_existing_stream(DEVICE_ID, CHANNEL_ID)
            hls = get_hls_url(data, stream_id)

    if hls:
        print(f"\nHLS URL: {hls}")
        print("\nPlay commands:")
        print(f"  VLC     : vlc '{hls}'")
        print(f"  ffplay  : ffplay '{hls}'")
        print(f"  Browser : Open directly (if CORS allows)")
    else:
        print("Failed to get stream URL")


if __name__ == "__main__":
    main()
