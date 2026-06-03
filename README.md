# Imou Camera Video Capture Guide

A comprehensive guide and working code examples for programmatically capturing video from Imou cameras using every available connection method.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Category A: Local Network Connection](#category-a-local-network-connection)
   - [A1. Direct RTSP Stream](#a1-direct-rtsp-stream)
   - [A2. RTSP via OpenCV](#a2-rtsp-via-opencv)
   - [A3. RTSP via NVR (Multi-Channel)](#a3-rtsp-via-nvr-multi-channel)
   - [A4. ONVIF Discovery](#a4-onvif-discovery)
   - [A5. ONVIF Stream URI](#a5-onvif-stream-uri)
   - [A6. HTTP Snapshot (JPEG)](#a6-http-snapshot-jpeg)
   - [A7. LAN Network Scanner](#a7-lan-network-scanner)
4. [Category B: Cloud Service Connection](#category-b-cloud-service-connection)
   - [B1. Official HTTP API (Raw)](#b1-official-http-api-raw)
   - [B2. Using `imouapi` Library](#b2-using-imouapi-library)
   - [B3. Using Official `pyimouapi` Library](#b3-using-official-pyimouapi-library)
   - [B4. Bind Live Stream (HLS)](#b4-bind-live-stream-hls)
   - [B5. Cloud Device Discovery](#b5-cloud-device-discovery)
   - [B6. Cloud Snapshots](#b6-cloud-snapshots)
   - [B7. Webhook Event Notifications](#b7-webhook-event-notifications)
   - [B8. Get KitToken for Browser Player](#b8-get-kittoken-for-browser-player)
   - [B9. WebVideo SDK Browser Player](#b9-webvideo-sdk-browser-player)
5. [Category C: Home Assistant Component Reference](#category-c-home-assistant-component-reference)
6. [Troubleshooting](./docs/03-troubleshooting.md)
7. [Browser Streaming Guide](./docs/06-browser-streaming.md)
8. [Glossary](./docs/04-glossary.md)

---

## Overview — Recommendation: Prefer Local RTSP

| Approach | Cost | Latency | Network | Recommended for |
|---|---|---|---|---|
| **★ A. Local RTSP** | **Free** | ~0.5s | Same LAN | **Always preferred** if server has LAN access to cameras |
| **B. Cloud API** | Traffic quota may incur cost | 3-10s | Any internet | Fallback when LAN access isn't possible |

**Rule of thumb:** If your server and camera are on the same network, use local RTSP (Category A). It's free, lower latency, and more reliable. The cloud API (Category B) is for remote access or when cameras are on a separate network.

Each approach includes a **working Python example** you can run immediately after filling in your credentials.

## Quick Start — RTSP (Recommended, Free)

If your server is on the same network as the camera, **RTSP is the simplest & cheapest option** — no cloud fees, no API keys, no traffic quotas.

```bash
# Install dependencies
pip install -r requirements.txt

# Edit the file to set your camera IP and password, then:
python examples/local/rtsp_direct.py      # Capture video via ffmpeg
python examples/local/rtsp_with_opencv.py # Frame-by-frame processing
```

**Not on the same network?** See [Category B](#category-b-cloud-service-connection) for cloud API access (requires AppId/AppSecret, video traffic may incur costs).

---

## Category A: Local Network Connection

These methods work when your computer/server is on the **same local network** as the camera or NVR. No internet or Imou account API keys are required.

### A1. Direct RTSP Stream

Capture raw RTSP stream using `ffmpeg` or `ffplay`. This is the simplest method for direct IP access.

**File:** [`examples/local/rtsp_direct.py`](./examples/local/rtsp_direct.py)

**Prerequisites:**
- Camera IP address
- Camera password / safety code
- `ffmpeg` installed

### A2. RTSP via OpenCV

Capture RTSP into Python for computer vision processing (frame-by-frame).

**File:** [`examples/local/rtsp_with_opencv.py`](./examples/local/rtsp_with_opencv.py)

**Prerequisites:**
- `pip install opencv-python`
- Camera IP and password

### A3. RTSP via NVR (Multi-Channel)

Access multiple cameras through a single NVR IP address using channel numbers.

**File:** [`examples/local/rtsp_nvr.py`](./examples/local/rtsp_nvr.py)

**Prerequisites:**
- NVR IP address
- NVR admin password
- Know the channel number for each camera

### A4. ONVIF Discovery

Automatically discover ONVIF-compatible cameras on your local network without knowing IPs.

**File:** [`examples/local/onvif_discovery.py`](./examples/local/onvif_discovery.py)

**Prerequisites:**
- `pip install onvif-zeep`
- Cameras with ONVIF enabled

### A5. ONVIF Stream URI

Query the camera's ONVIF service to get the official RTSP stream URL programmatically.

**File:** [`examples/local/onvif_stream.py`](./examples/local/onvif_stream.py)

**Prerequisites:**
- `pip install onvif-zeep`
- Camera IP, ONVIF port (usually 80 or 8080), username/password

### A6. HTTP Snapshot (JPEG)

Grab a single JPEG frame via HTTP instead of maintaining a continuous video stream.

**File:** [`examples/local/http_snapshot.py`](./examples/local/http_snapshot.py)

**Prerequisites:**
- Camera supports HTTP snapshot endpoint
- Often works on Dahua/Imou firmware at `/cgi-bin/snapshot.cgi`

### A7. LAN Network Scanner

Scan your entire subnet to find cameras with open RTSP ports (554) and test authentication.

**File:** [`examples/local/lan_scanner.py`](./examples/local/lan_scanner.py)

**Prerequisites:**
- `pip install python-nmap opencv-python`
- `nmap` installed on system

> **Full guide:** See [`docs/01-local-network.md`](./docs/01-local-network.md)

---

## Category B: Cloud Service Connection

These methods use the **Imou Open Platform** to access cameras remotely, reusing the same account from your Imou Life mobile app.

### B1. Official HTTP API (Raw)

Make raw HTTP calls to Imou's cloud API: authenticate, discover devices, and request live stream URLs.

**File:** [`examples/cloud/official_api_raw.py`](./examples/cloud/official_api_raw.py)

**Prerequisites:**
- AppId and AppSecret from https://open.imoulife.com
- Region endpoint URL

### B2. Using `imouapi` Library

Higher-level Python library that wraps the HTTP API with device abstractions.

**File:** [`examples/cloud/imouapi_library.py`](./examples/cloud/imouapi_library.py)

**Prerequisites:**
- `pip install imouapi`
- AppId and AppSecret

### B3. Using Official `pyimouapi` Library

The official library used by the Home Assistant integration.

**File:** [`examples/cloud/pyimouapi_example.py`](./examples/cloud/pyimouapi_example.py)

**Prerequisites:**
- `pip install pyimouapi`
- AppId and AppSecret

### B4. Bind Live Stream (HLS)

Programmatically bind a live stream to get an HLS URL (compatible with most players/browsers).

**File:** [`examples/cloud/bind_live_stream.py`](./examples/cloud/bind_live_stream.py)

**Prerequisites:**
- AppId and AppSecret
- Device ID from discovery

### B5. Cloud Device Discovery

List all devices bound to your Imou account via the cloud API.

**File:** [`examples/cloud/device_discovery.py`](./examples/cloud/device_discovery.py)

**Prerequisites:**
- AppId and AppSecret

### B6. Cloud Snapshots

Request a fresh snapshot image via the cloud API (device wakes up if dormant).

**File:** [`examples/cloud/cloud_snapshots.py`](./examples/cloud/cloud_snapshots.py)

**Prerequisites:**
- AppId and AppSecret
- Device ID

### B7. Webhook Event Notifications

Receive motion detection and alarm events via cloud webhooks instead of polling.

**File:** [`examples/cloud/webhook_events.py`](./examples/cloud/webhook_events.py)

**Prerequisites:**
- Publicly accessible URL for webhook receiver
- AppId and AppSecret

> **Full guide:** See [`docs/02-cloud-service.md`](./docs/02-cloud-service.md)

### B8. Get KitToken for Browser Player

Generate a device-specific kitToken for use with the WebVideo SDK browser player.

**File:** [`examples/cloud/get_kit_token.py`](./examples/cloud/get_kit_token.py)

**Prerequisites:**
- AppId and AppSecret
- Device ID from discovery

### B9. WebVideo SDK Browser Player

Browser-based streaming using the Imou WebVideo SDK (WebSocket RTSP over WASM).
Includes live view, PTZ, snapshot, recording, and two-way audio.

**Files:**
- Player page: [`examples/cloud/webvideo_player.html`](./examples/cloud/webvideo_player.html)
- Setup script: [`examples/cloud/setup_webvideo_sdk.sh`](./examples/cloud/setup_webvideo_sdk.sh)
- Node server: [`examples/cloud/webvideo_server.js`](./examples/cloud/webvideo_server.js)

> **Full guide:** See [`docs/06-browser-streaming.md`](./docs/06-browser-streaming.md)

---

## Category C: Home Assistant Component Reference

The `Imou-Home-Assistant.zip` contains a complete Home Assistant `custom_component`
(`imou_life`) using the official `pyimouapi` SDK. It demonstrates production-grade
integration patterns:

| Platform | Entities | Key File |
|----------|----------|----------|
| `camera` | Live HLS stream + snapshot | `camera.py` |
| `sensor` | Battery, storage, temperature, humidity | `sensor.py` |
| `switch` | Motion detect, close camera, white light, etc. | `switch.py` |
| `select` | Night vision mode, volume, device mode | `select.py` |
| `button` | PTZ (4 dirs), restart device, mute | `button.py` |
| `binary_sensor` | Door contact status | `binary_sensor.py` |
| `config_flow` | AppId/AppSecret input, region selection, options | `config_flow.py` |
| `coordinator` | Polling update coordinator (60s interval) | `coordinator.py` |

**SDK source:** https://github.com/Imou-OpenPlatform/Py-Imou-Open-Api (v1.2.7+)

---

## Troubleshooting

Common issues and fixes for each approach: [`docs/03-troubleshooting.md`](./docs/03-troubleshooting.md)

## Browser Streaming Guide

Detailed guide for the WebVideo SDK browser player: [`docs/06-browser-streaming.md`](./docs/06-browser-streaming.md)

## Glossary

Terms and abbreviations used throughout: [`docs/04-glossary.md`](./docs/04-glossary.md)

---

## License

MIT. Use at your own risk. Always secure your camera credentials.
