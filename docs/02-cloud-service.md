# Cloud Service Connection Guide

This guide covers all methods to programmatically capture video from Imou cameras using the **Imou Open Platform cloud API**.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting API Credentials](#getting-api-credentials)
3. [Region Endpoints](#region-endpoints)
4. [B1. Official HTTP API (Raw)](#b1-official-http-api-raw)
5. [B2. Using `imouapi` Library](#b2-using-imouapi-library)
6. [B3. Using Official `pyimouapi` Library](#b3-using-official-pyimouapi-library)
7. [B4. Bind Live Stream (HLS)](#b4-bind-live-stream-hls)
8. [B5. Cloud Device Discovery](#b5-cloud-device-discovery)
9. [B6. Cloud Snapshots](#b6-cloud-snapshots)
10. [B7. Webhook Event Notifications](#b7-webhook-event-notifications)
11. [Quota & Limits](#quota--limits)
12. [Choosing the Right Method](#choosing-the-right-method)

---

## Prerequisites

- Imou account (same as mobile app)
- Developer registration at https://open.imoulife.com
- AppId and AppSecret generated from the console

---

## Getting API Credentials

1. Visit https://open.imoulife.com
2. Sign in with your Imou account
3. Go to **Console > My App > App Info**
4. Create an application if you haven't already
5. Copy the **AppId** and **AppSecret**

> **Security:** Never commit AppSecret to public repositories. Use environment variables.

---

## Region Endpoints

Choose the endpoint matching where your Imou account was registered:

| Region | Endpoint |
|---|---|
| Singapore / Asia-Pacific | `https://openapi.easy4ip.com/openapi` |
| Frankfurt / Europe | `https://openapi-fra.easy4ip.com/openapi` |
| Oregon / Americas | `https://openapi-or.easy4ip.com/openapi` |
| China mainland | `https://openapi.easy4ip.com/openapi` |

---

## B1. Official HTTP API (Raw)

Direct HTTP POST calls to Imou's REST API. All requests must be signed.

**Authentication flow:**
1. Call `accessToken` with signed request (no token needed)
2. Receive `accessToken` valid for a limited time
3. Include `token` in subsequent request payloads

**Signature algorithm:**
```python
sign = md5(f"time:{timestamp},nonce:{nonce},appSecret:{APP_SECRET}")
```

**Python example:** [`examples/cloud/official_api_raw.py`](../examples/cloud/official_api_raw.py)

---

## B2. Using `imouapi` Library

Community Python library that wraps the HTTP API with high-level abstractions.

**Features:**
- Asyncio support
- Device and sensor classes
- Exception handling
- Automatic reconnection

**Install:** `pip install imouapi`

**Python example:** [`examples/cloud/imouapi_library.py`](../examples/cloud/imouapi_library.py)

---

## B3. Using Official `pyimouapi` Library

Official library maintained by Imou Open Platform team. Used in the Home Assistant integration.

**Install:** `pip install pyimouapi`

**Python example:** [`examples/cloud/pyimouapi_example.py`](../examples/cloud/pyimouapi_example.py)

---

## B4. Bind Live Stream (HLS)

Request a cloud-proxied HLS stream URL. This works from anywhere, not just local network.

**API flow:**
1. Call `bindDeviceLive` with `deviceId`, `channelId`, `streamId`
2. Receive JSON containing `streams[].hls` URL
3. Play the HLS URL in any compatible player

**Stream IDs:**
- `0` = HD main stream
- `1` = SD sub stream

**Python example:** [`examples/cloud/bind_live_stream.py`](../examples/cloud/bind_live_stream.py)

---

## B5. Cloud Device Discovery

List all devices bound to your account. Essential first step to get device IDs.

**API:** `deviceBaseList`

Returns:
- `deviceId` (required for all subsequent calls)
- `deviceModel`, `name`, `status`
- `ability` (capability flags)
- `channelNum`

**Python example:** [`examples/cloud/device_discovery.py`](../examples/cloud/device_discovery.py)

---

## B6. Cloud Snapshots

Request a JPEG snapshot through the cloud. The camera wakes from sleep if needed.

**API:** `deviceSnap`

Returns a temporary URL to download the image. URL expires after a short time.

**Python example:** [`examples/cloud/cloud_snapshots.py`](../examples/cloud/cloud_snapshots.py)

---

## B7. Webhook Event Notifications

Instead of polling, receive push notifications for events.

**Supported events:**
- Motion detection (`motionAlarm`)
- Human detection (`humanDetect`)
- Low battery
- Device offline/online
- Abnormal sound

**Setup:**
1. Expose a public HTTPS endpoint
2. Register it via `setMessageCallback`
3. Imou cloud POSTs event JSON to your URL

**Python example:** [`examples/cloud/webhook_events.py`](../examples/cloud/webhook_events.py)

---

## Quota & Limits

Cloud API usage consumes resource quotas under your AppId:

- **Video streaming** (live/playback) consumes streaming quota
- **API calls** consume API call quota
- Check your usage at: https://open.imoulife.com/consoleNew/resourceManage/myResource

Free tier limits apply. Upgrade or contact Imou for commercial use.

---

## Choosing the Right Method

| Use Case | Recommended Method |
|---|---|
| Full control, custom logic | B1. Raw HTTP API |
| Quick Python integration | B2. `imouapi` library |
| Home Assistant / official support | B3. `pyimouapi` library |
| Browser/web player playback | B4. HLS Live Stream |
| Find device IDs | B5. Cloud Discovery |
| Thumbnail without RTSP | B6. Cloud Snapshot |
| Real-time alerts | B7. Webhook Events |
