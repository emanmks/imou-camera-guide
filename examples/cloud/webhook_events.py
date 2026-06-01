"""
B7. Webhook Event Notifications

Receive motion detection and alarm events from Imou cloud via webhooks.
Instead of polling, Imou pushes events to your public URL.

Prerequisites:
    - A publicly accessible URL (use ngrok for local testing)
    - pip install flask requests

Setup:
    1. Run this script (it starts a web server)
    2. Expose it publicly: ngrok http 5000
    3. Register the webhook URL in Imou console or via API
"""

import hashlib
import hmac
import json
import random
import secrets
import time
from flask import Flask, request
import requests

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
BASE_URL = "https://openapi.easy4ip.com/openapi"
WEBHOOK_PORT = 5000
# Your public webhook URL (e.g., from ngrok)
WEBHOOK_URL = "https://your-ngrok-url.ngrok.io/webhook"
# =================================================

app = Flask(__name__)


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


def register_webhook():
    """Register webhook callback URL with Imou."""
    token = get_token()
    print(f"Registering webhook: {WEBHOOK_URL}")
    result = api_call(
        "setMessageCallback",
        {"callbackUrl": WEBHOOK_URL},
        token=token,
    )
    print(f"Webhook registered: {result}")


@app.route("/webhook", methods=["POST"])
def webhook_receiver():
    """Receive events from Imou cloud."""
    data = request.get_json(force=True, silent=True) or {}
    print("\n=== EVENT RECEIVED ===")
    print(json.dumps(data, indent=2))

    # Example event types:
    # - motionAlarm
    # - humanDetect
    # - lowBattery
    # - offline
    event_type = data.get("msgType")
    device_id = data.get("deviceId")
    print(f"Type: {event_type} | Device: {device_id}")
    print("======================\n")
    return "OK", 200


@app.route("/")
def index():
    return "Imou Webhook Receiver is running", 200


def main():
    print("Starting webhook receiver...")
    print(f"Register your webhook at: {WEBHOOK_URL}")
    try:
        register_webhook()
    except Exception as e:
        print(f"Webhook registration failed (may already be set): {e}")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)


if __name__ == "__main__":
    main()
