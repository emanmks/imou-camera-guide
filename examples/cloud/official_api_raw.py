"""
B1. Official HTTP API (Raw)

Make raw HTTP calls to Imou Open Platform API.
Demonstrates: access token auth, device discovery, live stream binding.

Key learnings from the official pyimouapi SDK:
  - Auth response may return currentDomain; ALL subsequent calls MUST use it
  - Token auto-refresh on TK1002 (token overdue)
  - Proper error code handling (SN1001, SN1004, TK1002, LV1001, LV1002)
  - Two device listing endpoints: deviceBaseList (legacy) and listDeviceDetailsByPage (SDK)
  - Stream binding: first try getLiveStreamInfo, then bindDeviceLive if LV1002
  - Snapshot: setDeviceSnapEnhanced returns a URL; wait ~3s before downloading

Imou API Docs: https://open.imoulife.com/book/en/http/develop.html
pyimouapi SDK:  https://github.com/Imou-OpenPlatform/Py-Imou-Open-Api
"""

import hashlib
import json
import logging
import random
import secrets
import time
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# ================= CONFIGURATION =================
APP_ID = "lc9831fd11e8b54fa8"
APP_SECRET = "7122dd4aac8942b7977a3accd4277b"

# Choose initial endpoint based on your account region:
#   Singapore:  openapi-sg.easy4ip.com
#   Frankfurt:  openapi-fra.easy4ip.com
#   Oregon:     openapi-or.easy4ip.com
#   China:      openapi.lechange.cn
# The SDK uses netloc only (no https:// prefix), and appends /openapi/{endpoint}.
INITIAL_API_URL = "openapi.easy4ip.com"
# =================================================


# ---------------------------------------------------------------------------
# ImouOpenApiClient — faithful reimplementation of the pyimouapi SDK pattern
# ---------------------------------------------------------------------------

class ImouOpenApiClient:
    """Async-style client (synchronous version) for Imou Open Platform API."""

    ERROR_CODES = {
        "0":     "Success",
        "TK1002": "Token overdue — auto-refreshing",
        "SN1001": "Invalid sign — check AppSecret and clock sync",
        "SN1004": "Invalid AppId or AppSecret",
        "DV1007": "Device offline",
        "LV1001": "Live stream already exists",
        "LV1002": "Live stream does not exist",
        "DV1030": "Device is sleeping (battery-powered)",
        "DV1049": "No storage medium",
    }

    def __init__(self, app_id: str, app_secret: str, api_url: str):
        self._app_id = app_id
        self._app_secret = app_secret
        self._api_url = api_url        # e.g. "openapi-sg.easy4ip.com"
        self._access_token: str | None = None

    # ---- public API ----

    def get_access_token(self) -> str:
        """Authenticate and store accessToken; handles currentDomain redirect."""
        data = self._request("/openapi/accessToken", {})
        self._access_token = data["accessToken"]

        # CRITICAL: SDK redirects all subsequent calls to currentDomain
        if "currentDomain" in data:
            raw = data["currentDomain"]
            if "://" not in raw:
                raw = f"https://{raw}"
            parsed = urlparse(raw)
            if parsed.netloc:
                _LOGGER.info("Redirecting to currentDomain: %s", parsed.netloc)
                self._api_url = parsed.netloc
            else:
                _LOGGER.warning("Could not parse currentDomain: %s", raw)

        expire = data.get("expireTime", "unknown")
        _LOGGER.info("Access token obtained (expires in %ss, API URL: %s)",
                     expire, self._api_url)
        return self._access_token

    def request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a signed POST request with auto token + auto refresh."""
        # If we don't have a token yet, get one (unless this IS the token call)
        if self._access_token is None and endpoint != "/openapi/accessToken":
            self.get_access_token()
        return self._request(endpoint, params)

    # ---- internal ----

    def _request(self, endpoint: str, params: dict | None = None) -> dict:
        payload = dict(params) if params else {}
        if self._access_token is not None and endpoint != "/openapi/accessToken":
            payload["token"] = self._access_token

        timestamp = round(time.time())
        nonce = secrets.token_urlsafe()
        sign = hashlib.md5(
            f"time:{timestamp},nonce:{nonce},appSecret:{self._app_secret}".encode("utf-8")
        ).hexdigest()
        request_id = str(random.randint(1, 100000))

        body = {
            "system": {
                "ver": "1.0",
                "sign": sign,
                "appId": self._app_id,
                "time": timestamp,
                "nonce": nonce,
            },
            "params": payload,
            "id": request_id,
        }

        url = f"https://{self._api_url}{endpoint}"
        _LOGGER.debug("POST %s", url)

        resp = requests.post(url, json=body, timeout=30)
        resp.raise_for_status()
        response_body = resp.json()

        # Parse result envelope
        result = response_body.get("result", {})
        code = result.get("code", "")
        msg = result.get("msg", "Unknown error")
        data = result.get("data", {})

        if code != "0":
            self._log_error(code, msg, endpoint)

            # TK1002: token overdue → auto-refresh & retry
            if code == "TK1002":
                _LOGGER.info("Token expired — refreshing and retrying %s", endpoint)
                self._access_token = None
                return self._request(endpoint, params)

            if code in ("SN1001", "SN1004"):
                raise ValueError(f"Auth failure [{code}]: {msg}. Check AppId/AppSecret and clock sync.")

            if code in ("LV1002", "LV1001", "DV1007", "DV1030", "DV1049"):
                _LOGGER.warning("Expected business error [%s]: %s", code, msg)
                return {}

            raise ValueError(f"API error [{code}]: {msg}")

        return data

    def _log_error(self, code: str, msg: str, endpoint: str) -> None:
        known = self.ERROR_CODES.get(code, "Unknown error code")
        _LOGGER.warning("API %s → [%s] %s (%s)", endpoint, code, msg, known)


# ---------------------------------------------------------------------------
# Convenience helpers using the client
# ---------------------------------------------------------------------------

def discover_devices(client: ImouOpenApiClient):
    """List all bound devices (SDK-compatible endpoint)."""
    _LOGGER.info("\n--- Device discovery ---")
    # The SDK uses listDeviceDetailsByPage with pagination
    data = client.request("/openapi/listDeviceDetailsByPage", {
        "page": 1,
        "pageSize": 50,
    })
    devices = data.get("deviceList", [])
    _LOGGER.info("Found %d device(s)", len(devices))
    for d in devices:
        channels = d.get("channelList", [])
        ch_info = ", ".join(
            f"{c['channelId']}:{c['channelName']}" for c in channels
        ) if channels else "(no channel info)"
        _LOGGER.info(
            "  %s | %s | %s | channels=[%s]",
            d.get("deviceId"),
            d.get("deviceName"),
            d.get("deviceStatus"),
            ch_info,
        )
    return devices


def bind_or_get_stream(client: ImouOpenApiClient, device_id: str, channel_id: str = "0", stream_id: int = 0):
    """
    Smart stream binding matching the pyimouapi SDK flow:
      1. Try getLiveStreamInfo
      2. If LV1002 (no live), call bindDeviceLive
      3. If LV1001 (already exists after bind), retry getLiveStreamInfo
    Returns the HLS URL or None.
    """
    # Step 1: try existing stream
    try:
        data = client.request("/openapi/getLiveStreamInfo", {
            "deviceId": device_id,
            "channelId": channel_id,
        })
        if data and data.get("streams"):
            return _extract_hls(data, stream_id)
    except ValueError:
        pass

    # Step 2: bind new stream
    _LOGGER.info("No existing stream, binding new one...")
    try:
        data = client.request("/openapi/bindDeviceLive", {
            "deviceId": device_id,
            "channelId": channel_id,
            "streamId": stream_id,
        })
        if data and data.get("streams"):
            return _extract_hls(data, stream_id)
    except ValueError as e:
        # LV1001: already exists — query again
        if "LV1001" in str(e):
            _LOGGER.info("Stream already exists, querying...")
            data = client.request("/openapi/getLiveStreamInfo", {
                "deviceId": device_id,
                "channelId": channel_id,
            })
            if data and data.get("streams"):
                return _extract_hls(data, stream_id)
        raise

    return None


def _extract_hls(data: dict, preferred_stream_id: int = 0) -> str | None:
    """Extract HLS URL from stream data, preferring matching streamId."""
    streams = data.get("streams", [])
    if not streams:
        return None
    # Prefer the requested streamId
    for s in streams:
        if s.get("streamId") == preferred_stream_id:
            return s.get("hls")
    # Fallback to first
    return streams[0].get("hls")


def request_snapshot(client: ImouOpenApiClient, device_id: str, channel_id: str = "0", wait: int = 3):
    """Trigger a cloud snapshot and download it (matching SDK pattern)."""
    _LOGGER.info("Requesting snapshot via setDeviceSnapEnhanced...")
    data = client.request("/openapi/setDeviceSnapEnhanced", {
        "deviceId": device_id,
        "channelId": channel_id,
    })
    url = data.get("url")
    if not url:
        _LOGGER.warning("No snapshot URL returned: %s", data)
        return None

    # SDK waits before downloading
    _LOGGER.info("Snapshot URL obtained, waiting %ds before download...", wait)
    time.sleep(wait)

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    filename = f"snapshot_{device_id}.jpg"
    with open(filename, "wb") as f:
        f.write(resp.content)
    _LOGGER.info("Snapshot saved: %s (%d bytes)", filename, len(resp.content))
    return filename


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # 1. Init client (authenticates on first request)
    client = ImouOpenApiClient(APP_ID, APP_SECRET, INITIAL_API_URL)

    # 2. Discover devices
    devices = discover_devices(client)
    if not devices:
        _LOGGER.warning("No devices found. Ensure cameras are bound to your Imou account.")
        return

    # 3. Get live stream for first device's first channel
    first = devices[0]
    dev_id = first["deviceId"]
    channels = first.get("channelList", [])
    ch_id = channels[0]["channelId"] if channels else "0"

    hls_url = bind_or_get_stream(client, dev_id, ch_id, stream_id=0)
    if hls_url:
        _LOGGER.info("\nHLS URL: %s", hls_url)
        _LOGGER.info("Play with: ffplay '%s'", hls_url)

    # 4. Take a snapshot
    request_snapshot(client, dev_id, ch_id, wait=3)


if __name__ == "__main__":
    main()
