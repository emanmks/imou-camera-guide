"""
B6. Cloud Snapshots

Request a fresh snapshot image via the Imou cloud API.
Matches the pyimouapi SDK pattern:
  1. Call setDeviceSnapEnhanced → returns presigned OSS URL
  2. Wait N seconds for camera to capture
  3. HTTP GET the URL, save as JPEG

The device will wake up if it is in dormant/sleep mode.

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
INITIAL_API_URL = "openapi.easy4ip.com"
OUTPUT_FILE = "cloud_snapshot.jpg"
SNAP_WAIT_SECONDS = 3  # seconds to wait for camera to capture
# =================================================


class SimpleApiClient:
    def __init__(self, app_id, app_secret, api_url):
        self._app_id = app_id
        self._app_secret = app_secret
        self._api_url = api_url
        self._token = None

    def _sign(self, ts, nonce):
        return hashlib.md5(
            f"time:{ts},nonce:{nonce},appSecret:{self._app_secret}".encode()
        ).hexdigest()

    def _request(self, endpoint, params=None):
        payload = dict(params) if params else {}
        if self._token is not None and endpoint != "/openapi/accessToken":
            payload["token"] = self._token
        ts = round(time.time())
        nonce = secrets.token_urlsafe()
        body = {
            "system": {"ver": "1.0", "sign": self._sign(ts, nonce),
                       "appId": self._app_id, "time": ts, "nonce": nonce},
            "params": payload,
            "id": str(random.randint(1, 100000)),
        }
        r = requests.post(f"https://{self._api_url}{endpoint}", json=body, timeout=30)
        r.raise_for_status()
        resp = r.json()
        result = resp.get("result", {})
        code = result.get("code", "")
        msg = result.get("msg", "")
        data = result.get("data", {})
        if code != "0":
            if code == "TK1002":
                self._token = None
                return self._request(endpoint, params)
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
                self._api_url = parsed.netloc
        return self._token


def main():
    client = SimpleApiClient(APP_ID, APP_SECRET, INITIAL_API_URL)
    client.authenticate()

    _LOGGER.info("Requesting snapshot via setDeviceSnapEnhanced...")
    data = client._request("/openapi/setDeviceSnapEnhanced", {
        "deviceId": DEVICE_ID,
        "channelId": CHANNEL_ID,
    })
    url = data.get("url")
    if not url:
        _LOGGER.error("No snapshot URL in response: %s", data)
        return

    print(f"Snapshot URL: {url}")

    # SDK pattern: wait N seconds before downloading
    _LOGGER.info("Waiting %ds for camera to capture...", SNAP_WAIT_SECONDS)
    time.sleep(SNAP_WAIT_SECONDS)

    _LOGGER.info("Downloading snapshot...")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with open(OUTPUT_FILE, "wb") as f:
        f.write(r.content)
    print(f"Saved to {OUTPUT_FILE} ({len(r.content)} bytes)")


if __name__ == "__main__":
    main()
