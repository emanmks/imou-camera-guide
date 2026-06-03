"""
B8. Get KitToken for WebVideo SDK Browser Streaming

The Imou WebVideo SDK (imou-player.js) uses a WebSocket-based RTSP protocol
decoded via WASM — NOT HLS. It requires a device-specific kitToken obtained
from the getKitToken API.

Flow:
  1. Authenticate: AppId + AppSecret → accessToken + currentDomain
  2. Get kitToken: accessToken + deviceId + channelId + type → kitToken
  3. Pass kitToken to imouPlayer() in the browser

The kitToken is valid for 2 hours. Cache it server-side for 1 hour.

Prerequisites:
    pip install requests

WebVideo SDK files (in imou-webvideo-sdk-demo-for-lightapp.zip):
    - imou-player.js   (core WASM-based WebSocket RTSP player)
    - imou-player.css  (player styles)
    - WasmLib/         (WebAssembly decoder binaries)
"""

import hashlib
import json
import logging
import random
import secrets
import time
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
_LOGGER = logging.getLogger(__name__)

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
INITIAL_API_URL = "openapi.easy4ip.com"

# Device to generate kitToken for (from discovery)
DEVICE_ID = "YOUR_DEVICE_ID"
CHANNEL_ID = "0"
# Permission type: 0=All, 1=Live, 2=Playback, 6=PTZ
TOKEN_TYPE = 0
# =================================================


class ImouClient:
    """Synchronous Imou Open Platform API client."""

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
                _LOGGER.info("API domain: %s", self._api_url)
        return self._token


def main():
    client = ImouClient(APP_ID, APP_SECRET, INITIAL_API_URL)
    client.authenticate()

    # 1. Discover devices (listDeviceDetailsByPage — SDK endpoint)
    _LOGGER.info("\n=== Device Discovery ===")
    data = client._request("/openapi/listDeviceDetailsByPage", {
        "page": 1, "pageSize": 50,
    })
    devices = data.get("deviceList", [])
    for d in devices:
        channels = d.get("channelList", [])
        ch_names = ", ".join(f"{c['channelId']}:{c['channelName']}" for c in channels)
        _LOGGER.info("  %s | %s | %s", d.get("deviceId"), d.get("deviceName"), ch_names)

    # 2. Get kitToken for the specified device
    _LOGGER.info("\n=== kitToken Generation ===")
    _LOGGER.info("Device: %s, Channel: %s, Type: %s", DEVICE_ID, CHANNEL_ID, TOKEN_TYPE)

    kit_data = client._request("/openapi/getKitToken", {
        "deviceId": DEVICE_ID,
        "channelId": CHANNEL_ID,
        "type": str(TOKEN_TYPE),
    })
    kit_token = kit_data.get("kitToken")
    expire = kit_data.get("expireTime", 7200)

    if not kit_token:
        _LOGGER.error("Failed to get kitToken")
        return

    print(f"\n{'='*60}")
    print(f"  kitToken    : {kit_token}")
    print(f"  Expires in  : {expire}s ({expire//60} min)")
    print(f"  API Domain  : {client._api_url}")
    print(f"  Device ID   : {DEVICE_ID}")
    print(f"  Channel ID  : {CHANNEL_ID}")
    print(f"{'='*60}")

    # 3. Generate an HTML snippet for the browser player
    html_snippet = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Imou WebVideo Player</title>
  <link href="https://cdn.jsdelivr.net/gh/Imou-OpenPlatform/imou-player@latest/imou-player.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/gh/Imou-OpenPlatform/imou-player@latest/imou-player.js"></script>
</head>
<body>
  <div id="player" style="width:800px;height:500px;"></div>
  <script>
    // NOTE: Copy WasmLib/ directory next to this HTML file for WASM decoding.
    // Download from: https://github.com/Imou-OpenPlatform/imou-player
    const player = new imouPlayer({{
      id: "player",
      width: 800,
      height: 500,
      deviceId: "{DEVICE_ID}",
      channelId: "{CHANNEL_ID}",
      token: "{kit_token}",
      type: 1,
      streamId: 0,
      recordType: "cloud",
      muted: false,
      controls: true,
      WasmLibPath: "WasmLib/",
      handleError: (err) => console.error("Player error:", err),
      handleCallBack: (event) => console.log("Player event:", event),
    }});
  </script>
</body>
</html>"""

    print("\n=== Browser HTML Snippet ===")
    print(html_snippet)


if __name__ == "__main__":
    main()
