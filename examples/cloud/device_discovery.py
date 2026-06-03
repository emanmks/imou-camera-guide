"""
B5. Cloud Device Discovery

List all devices bound to your Imou account via the cloud API.
Uses both available endpoints:
  - listDeviceDetailsByPage (SDK/preferred — more fields)
  - deviceBaseList (legacy — also works with correct params)

Shows device IDs, models, channels, online status, and capabilities.

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
INITIAL_API_URL = "openapi.easy4ip.com"
# =================================================


def make_api(app_id, app_secret):
    """Factory: returns a simple authenticated request helper."""
    _token = None
    _api_url = INITIAL_API_URL

    def _sign(ts, nonce):
        return hashlib.md5(f"time:{ts},nonce:{nonce},appSecret:{app_secret}".encode()).hexdigest()

    def _req(endpoint, params=None):
        nonlocal _token, _api_url
        payload = dict(params) if params else {}
        if _token is not None and endpoint != "/openapi/accessToken":
            payload["token"] = _token
        ts = round(time.time())
        nonce = secrets.token_urlsafe()
        body = {
            "system": {"ver": "1.0", "sign": _sign(ts, nonce), "appId": app_id, "time": ts, "nonce": nonce},
            "params": payload,
            "id": str(random.randint(1, 100000)),
        }
        r = requests.post(f"https://{_api_url}{endpoint}", json=body, timeout=30)
        r.raise_for_status()
        resp = r.json()
        result = resp.get("result", {})
        code = result.get("code", "")
        msg = result.get("msg", "")
        data = result.get("data", {})
        if code != "0":
            if code == "TK1002":
                _token = None
                return _req(endpoint, params)
            raise ValueError(f"[{code}] {msg}")
        return data

    # Authenticate
    data = _req("/openapi/accessToken", {})
    _token = data.get("accessToken")
    if "currentDomain" in data:
        raw = data["currentDomain"]
        if "://" not in raw:
            raw = f"https://{raw}"
        parsed = urlparse(raw)
        if parsed.netloc:
            _api_url = parsed.netloc
            _LOGGER.info("Using API domain: %s", _api_url)
    return _req


def main():
    api = make_api(APP_ID, APP_SECRET)

    # --- Endpoint 1: listDeviceDetailsByPage (official SDK endpoint) ---
    _LOGGER.info("\n--- listDeviceDetailsByPage (SDK/preferred) ---")
    data = api("/openapi/listDeviceDetailsByPage", {"page": 1, "pageSize": 50})
    devices = data.get("deviceList", [])
    _LOGGER.info("Found %d device(s)", len(devices))

    for d in devices:
        print(f"\n  Device ID    : {d.get('deviceId')}")
        print(f"  Name         : {d.get('deviceName')}")
        print(f"  Model        : {d.get('deviceModel', 'unknown')}")
        print(f"  Status       : {d.get('deviceStatus')}")
        print(f"  Version      : {d.get('deviceVersion', 'unknown')}")
        print(f"  Brand        : {d.get('brand', 'unknown')}")
        channels = d.get("channelList", [])
        print(f"  Channels     : {len(channels)}")
        for ch in channels:
            print(f"    ├─ ID: {ch.get('channelId')}, Name: {ch.get('channelName')}, "
                  f"Status: {ch.get('channelStatus')}, Ability: {ch.get('channelAbility', 'N/A')}")

    # --- Endpoint 2: deviceBaseList (legacy, also works) ---
    _LOGGER.info("\n--- deviceBaseList (legacy endpoint) ---")
    data2 = api("/openapi/deviceBaseList", {
        "bindId": -1,
        "limit": 50,
        "type": "bindAndShare",
        "needApInfo": True,
    })
    devices2 = data2.get("deviceList", [])
    _LOGGER.info("Found %d device(s)", len(devices2))
    for d in devices2:
        chs = d.get("channels", [])
        print(f"\n  Device ID : {d.get('deviceId')}")
        print(f"  Channels  : {[c.get('channelName') for c in chs]}")


if __name__ == "__main__":
    main()
