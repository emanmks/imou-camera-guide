# Cloud Service Connection Guide (Fallback Option)

This guide covers all methods to programmatically capture video from Imou cameras
using the **Imou Open Platform cloud API**.

> **⚠️ Prefer Local RTSP when possible.** If your server has LAN access to the cameras,
> local RTSP (Category A) is **free**, lower latency (~0.5s vs 3-10s), and has no
> traffic quotas or API rate limits. Use the cloud API **only when**:
> - The server cannot reach the cameras on the local network
> - You need remote access across different networks
> - You need cloud features (webhooks, cloud snapshots, browser streaming)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting API Credentials](#getting-api-credentials)
3. [API Fundamentals](#api-fundamentals)
4. [B1. Official HTTP API (Raw)](#b1-official-http-api-raw)
5. [B2. Using `imouapi` Library](#b2-using-imouapi-library)
6. [B3. Using Official `pyimouapi` Library](#b3-using-official-pyimouapi-library)
7. [B4. Bind Live Stream (HLS)](#b4-bind-live-stream-hls)
8. [B5. Cloud Device Discovery](#b5-cloud-device-discovery)
9. [B6. Cloud Snapshots](#b6-cloud-snapshots)
10. [B7. Webhook Event Notifications](#b7-webhook-event-notifications)
11. [B8. Get KitToken for Browser Player](#b8-get-kittoken-for-browser-player)
12. [B9. WebVideo SDK Browser Player](#b9-webvideo-sdk-browser-player)
13. [Quota & Limits](#quota--limits)
14. [Live Streaming Console (GUI)](#live-streaming-console-gui)
15. [Choosing the Right Method](#choosing-the-right-method)

---

## Prerequisites

- Imou account (same as mobile app)
- Developer registration at https://open.imoulife.com
- AppId and AppSecret generated from the console
- Cameras bound to your Imou account (via Imou Life app)

---

## Getting API Credentials

1. Visit https://open.imoulife.com
2. Sign in with your Imou account
3. Go to **Console > My App > App Info**
4. Create an application if you haven't already
5. Copy the **AppId** and **AppSecret**

> **Security:** Never commit AppSecret to public repositories. Use environment variables.

---

## API Fundamentals

### Request Format

All Imou Open API requests are HTTP POST with JSON body containing a `system`
block (with MD5 signature) and a `params` block:

```json
{
  "system": {
    "ver": "1.0",
    "sign": "<md5 hash>",
    "appId": "lcxxxxxxxxxxxxxx",
    "time": <unix_timestamp>,
    "nonce": "<random>"
  },
  "params": { ... },
  "id": "<request_id>"
}
```

### Signature Algorithm

```python
sign = md5(f"time:{timestamp},nonce:{nonce},appSecret:{APP_SECRET}")
```

### Authentication Flow

1. POST to `/openapi/accessToken` with signed system block (no token needed)
2. Response returns `accessToken` and **optionally `currentDomain`**
3. **CRITICAL:** If `currentDomain` is present, ALL subsequent API calls MUST
   use that domain instead of the initial endpoint
4. Include `token` in the `params` of every subsequent request
5. On `TK1002` error (token overdue), re-authenticate and retry

### Region Endpoints

| Region | Initial Endpoint | API URL (netloc) |
|--------|-----------------|-------------------|
| Singapore / Asia-Pacific | `openapi.easy4ip.com` | `openapi-sg.easy4ip.com` |
| Frankfurt / Europe | `openapi-fra.easy4ip.com` | `openapi-fra.easy4ip.com` |
| Oregon / Americas | `openapi-or.easy4ip.com` | `openapi-or.easy4ip.com` |
| Moscow / Russia | `openapi-fk.easy4ip.com` | `openapi-fk.easy4ip.com` |
| China mainland | `openapi.lechange.cn` | `openapi.lechange.cn` |

> The SDK uses the netloc format (`openapi-sg.easy4ip.com`) and constructs URLs
> as `https://{netloc}/openapi/{endpoint}`.

### Error Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `TK1002` | Token overdue — re-authenticate |
| `SN1001` | Invalid sign — check AppSecret and clock sync |
| `SN1004` | Invalid AppId or AppSecret |
| `DV1007` | Device offline |
| `DV1030` | Device is sleeping (battery-powered) |
| `DV1049` | No storage medium |
| `LV1001` | Live stream already exists |
| `LV1002` | Live stream does not exist |

### API Endpoints Summary

| Endpoint | Purpose |
|----------|---------|
| `/openapi/accessToken` | Get access token |
| `/openapi/listDeviceDetailsByPage` | List devices (SDK/preferred) |
| `/openapi/deviceBaseList` | List devices (legacy) |
| `/openapi/bindDeviceLive` | Create HLS live stream |
| `/openapi/getLiveStreamInfo` | Query existing HLS stream |
| `/openapi/setDeviceSnapEnhanced` | Trigger cloud snapshot |
| `/openapi/setMessageCallback` | Register webhook |
| `/openapi/getAlarmMessage` | Query alarm events |
| `/openapi/deviceOnline` | Check online status |
| `/openapi/deviceStorage` | Get storage info |
| `/openapi/restartDevice` | Reboot device |
| `/openapi/controlMovePTZ` | PTZ control |
| `/openapi/getDeviceCameraStatus` | Get switch status |
| `/openapi/setDeviceCameraStatus` | Set switch status |
| `/openapi/getNightVisionMode` | Get night vision mode |
| `/openapi/setNightVisionMode` | Set night vision mode |
| `/openapi/getDevicePowerInfo` | Get battery/power info |
| `/openapi/deviceSdcardStatus` | SD card status |
| `/openapi/getKitToken` | Get kitToken for browser player |
| `/openapi/wakeUpDevice` | Wake battery-powered device |

---

## B1. Official HTTP API (Raw)

Direct HTTP POST calls to Imou's REST API. All requests must be signed.

**Key improvements (from pyimouapi SDK v1.2.7 analysis):**
- Handles `currentDomain` redirect from auth response
- Auto-refreshes token on `TK1002`
- Two-step stream binding: `getLiveStreamInfo` → `bindDeviceLive` → retry
- Snapshot wait time (3s default) before downloading
- Proper error code handling

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

**GitHub:** https://github.com/user2684/imouapi

---

## B3. Using Official `pyimouapi` Library

Official library maintained by Imou Open Platform team. Used in the Home Assistant
integration (`custom_components/imou_life`).

**Install:** `pip install pyimouapi`

**Python example:** [`examples/cloud/pyimouapi_example.py`](../examples/cloud/pyimouapi_example.py)

**GitHub:** https://github.com/Imou-OpenPlatform/Py-Imou-Open-Api

**Key features from v1.2.7:**
- `ImouOpenApiClient` — signed request handling, auto token refresh, currentDomain redirect
- `ImouDeviceManager` — device CRUD, PTZ, night vision, storage, snap, stream, IoT properties
- `ImouHaDeviceManager` — HA-level orchestration with ability-based and ref-based entity configuration
- All 22 API endpoints implemented
- Error code handling for all known codes
- IoT Things Model support with expression-based sensor evaluation

---

## B4. Bind Live Stream (HLS)

Request a cloud-proxied HLS stream URL. This works from anywhere, not just local network.

**API flow (from pyimouapi SDK):**
1. Call `getLiveStreamInfo` with `deviceId`, `channelId`
2. If `LV1002` (no live), call `bindDeviceLive` with `deviceId`, `channelId`, `streamId`
3. If `LV1001` (already exists) after bind, retry `getLiveStreamInfo`
4. Response contains `streams[].hls` — select by `streamId` (0=HD, 1=SD) and protocol (http/https)

**Stream IDs:**
- `0` = HD main stream
- `1` = SD sub stream

**Python example:** [`examples/cloud/bind_live_stream.py`](../examples/cloud/bind_live_stream.py)

---

## B5. Cloud Device Discovery

List all devices bound to your account. Essential first step to get device IDs.

**Two available endpoints:**

| Endpoint | Params | Notes |
|----------|--------|-------|
| `listDeviceDetailsByPage` | `{"page": 1, "pageSize": 50}` | **Preferred** — returns `channelList`, `deviceStatus`, `brand`, `deviceModel`, `deviceVersion`, `productId`, `deviceAbility` |
| `deviceBaseList` | `{"bindId": -1, "limit": 50, "type": "bindAndShare", "needApInfo": true}` | Legacy — also works |

**Python example:** [`examples/cloud/device_discovery.py`](../examples/cloud/device_discovery.py)

---

## B6. Cloud Snapshots

Request a JPEG snapshot through the cloud. The camera wakes from sleep if needed.

**API flow (from pyimouapi SDK):**
1. Call `setDeviceSnapEnhanced` with `deviceId`, `channelId`
2. Response returns a presigned OSS URL
3. Wait `SNAP_WAIT_SECONDS` (default 3) for camera to capture
4. HTTP GET the URL, save as JPEG

**Note:** `deviceSnap` is deprecated — always use `setDeviceSnapEnhanced`.

**Python example:** [`examples/cloud/cloud_snapshots.py`](../examples/cloud/cloud_snapshots.py)

---

## B7. Webhook Event Notifications

Instead of polling, receive push notifications for events.

**Supported event flags:** `alarm`, `deviceStatus`

**Setup:**
1. Expose a public HTTPS endpoint
2. Register it via `setMessageCallback` with `callbackFlag` and `status="on"`
3. Imou cloud POSTs event JSON to your URL

**Python example:** [`examples/cloud/webhook_events.py`](../examples/cloud/webhook_events.py)

---

## B8. Get KitToken for Browser Player

Generate a device-specific `kitToken` for use with the WebVideo SDK browser player
(`imou-player.js`). This is the first step for browser-based WebSocket RTSP streaming.

**API:** `POST /openapi/getKitToken`

**Parameters:**
- `token` — accessToken from authentication
- `deviceId` — device serial number
- `channelId` — channel number (e.g., "0")
- `type` — permission type: `0`=All, `1`=Live, `2`=Playback, `6`=PTZ

**Response:** Returns `kitToken` (valid 2 hours) and `expireTime` (seconds).

**Python example:** [`examples/cloud/get_kit_token.py`](../examples/cloud/get_kit_token.py)

---

## B9. WebVideo SDK Browser Player

Use the Imou WebVideo SDK (`imou-player.js`) for browser-based live viewing with
PTZ, snapshot, recording, and two-way audio. Unlike HLS, this uses a
WebSocket-based RTSP tunnel decoded via WebAssembly.

**Files:**
- Browser page: [`examples/cloud/webvideo_player.html`](../examples/cloud/webvideo_player.html)
- Setup script: [`examples/cloud/setup_webvideo_sdk.sh`](../examples/cloud/setup_webvideo_sdk.sh)
- Node server: [`examples/cloud/webvideo_server.js`](../examples/cloud/webvideo_server.js)

**Full guide:** [`docs/06-browser-streaming.md`](./docs/06-browser-streaming.md)

---

## Quota & Limits

Cloud API usage consumes resource quotas under your AppId:

- **Video streaming** (live/playback) consumes streaming quota
- **API calls** consume API call quota
- **Snapshot** requests consume snapshot quota
- **Check & purchase** at: https://open.imoulife.com/consoleNew/resourceManage/myResource
  If quota is zero or insufficient, streaming and snapshot APIs will silently fail.
  Purchase video traffic or bandwidth from the console before going live.

Free tier limits apply. Upgrade or contact Imou for commercial use.

## Live Streaming Console (GUI)

As an alternative to the API, the Imou console provides a GUI for live stream management:
https://open.imoulife.com/consoleNew/vas/live

Features:
- Get device live stream URLs manually
- Set streaming time schedules
- Configure custom H5 player pages (title, description, logo, cover, resolution, encryption)
- Generate QR codes for sharing

Useful for testing before writing code, or for simple single-stream scenarios.

---

## Choosing the Right Method

> **#1 Pick — Local RTSP:** If your server has LAN access to the cameras, use the
> [local RTSP examples](../README.md#category-a-local-network-connection) instead.
> It's free, lower latency, and more reliable. Only use the cloud API when local
> access isn't possible.

| Use Case | Cloud Method (fallback) |
|----------|------------------------|
| Same-network capture (preferred) | ★ Local RTSP (free, Category A) |
| Full control, custom logic | B1. Raw HTTP API |
| Quick Python integration | B2. `imouapi` library |
| Home Assistant / official support | B3. `pyimouapi` library |
| Browser/web player playback | B9. WebVideo SDK |
| Find device IDs | B5. Cloud Discovery |
| Thumbnail without RTSP | B6. Cloud Snapshot |
| Real-time alerts | B7. Webhook Events |
| Browser player token | B8. getKitToken |
| Server-side HLS stream | B4. HLS Live Stream |
