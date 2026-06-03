"""
B7. Webhook Event Notifications

Receive motion detection and alarm events from Imou cloud via webhooks.
Instead of polling, the Imou cloud pushes events to your public URL.

The pyimouapi SDK does not provide webhook helpers — the setMessageCallback
API is called directly. Requires callbackFlag and status parameters.

Prerequisites:
    - A publicly accessible URL (use ngrok for local testing)
    - pip install flask requests

Setup:
    1. Run this script (starts a web server on port 5000)
    2. Expose it publicly: ngrok http 5000
    3. Script registers the webhook URL with Imou automatically
"""

import hashlib
import logging
import random
import secrets
import time
from urllib.parse import urlparse

import requests
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
INITIAL_API_URL = "openapi.easy4ip.com"
WEBHOOK_PORT = 5000
WEBHOOK_URL = "https://your-ngrok-url.ngrok.io/webhook"
# =================================================

app = Flask(__name__)


# ---- API client (matching SDK patterns) ----

class ApiClient:
    def __init__(self, app_id, app_secret, api_url):
        self._app_id = app_id
        self._app_secret = app_secret
        self._api_url = api_url
        self._token = None

    def _sign(self, ts, nonce):
        return hashlib.md5(
            f"time:{ts},nonce:{nonce},appSecret:{self._app_secret}".encode()
        ).hexdigest()

    def call(self, endpoint, params=None):
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
                return self.call(endpoint, params)
            raise ValueError(f"[{code}] {msg}")
        return data

    def authenticate(self):
        data = self.call("/openapi/accessToken", {})
        self._token = data.get("accessToken")
        if "currentDomain" in data:
            raw = data["currentDomain"]
            if "://" not in raw:
                raw = f"https://{raw}"
            parsed = urlparse(raw)
            if parsed.netloc:
                self._api_url = parsed.netloc
        return self._token


api = ApiClient(APP_ID, APP_SECRET, INITIAL_API_URL)


# ---- Webhook registration ----

def register_webhook():
    api.authenticate()
    _LOGGER.info("Registering webhook: %s", WEBHOOK_URL)
    result = api.call("/openapi/setMessageCallback", {
        "callbackFlag": "alarm,deviceStatus",
        "callbackUrl": WEBHOOK_URL,
        "status": "on",
    })
    _LOGGER.info("Webhook registered: %s", result)


# ---- Flask receiver ----

@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    data = request.get_json(force=True, silent=True) or {}
    print("\n=== EVENT RECEIVED ===")
    print(data)
    event_type = data.get("msgType")
    device_id = data.get("deviceId")
    print(f"Type: {event_type} | Device: {device_id}")
    print("======================\n")
    return "OK", 200


@app.route("/")
def index():
    return "Imou Webhook Receiver is running", 200


# ---- Main ----

def main():
    print(f"Starting webhook receiver on port {WEBHOOK_PORT}...")
    print(f"Register your webhook at: {WEBHOOK_URL}")
    try:
        register_webhook()
    except Exception as e:
        _LOGGER.warning("Webhook registration failed (may already be set): %s", e)
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)


if __name__ == "__main__":
    main()
