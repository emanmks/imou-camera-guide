# Troubleshooting

Common issues and solutions for each connection approach.

---

## Local Network Issues

### RTSP: Cannot open stream / Connection refused
- **Cause:** Camera blocking RTSP or wrong IP/password
- **Fix:**
  - Verify camera IP (ping it)
  - Check password: use Safety Code from camera sticker, or custom password if changed
  - Ensure RTSP/ONVIF is enabled in camera settings (via Imou app or web UI)
  - Try `subtype=1` (SD) if main stream fails

### RTSP: Works in VLC but not OpenCV
- **Cause:** OpenCV built without FFMPEG support
- **Fix:** Install opencv-python: `pip install opencv-python`
- **Alternative:** Use `ffmpeg` subprocess piping to OpenCV

### ONVIF: No devices found
- **Cause:** ONVIF disabled or cameras on different subnet/VLAN
- **Fix:** Enable ONVIF in camera network settings. WS-Discovery uses broadcast, so it won't cross routers.

### HTTP Snapshot: 401 Unauthorized
- **Cause:** Authentication method mismatch
- **Fix:** Try Digest auth instead of Basic. Some firmware requires Digest.

### NVR: Channel returns black screen
- **Cause:** Camera not plugged into that NVR channel, or channel numbering starts at 0
- **Fix:** Verify physical connections. Try channel 0 if 1 fails (firmware dependent).

---

## Cloud Service Issues

### API: "Invalid sign" or "Unauthorized"
- **Cause:** Wrong AppSecret, clock skew, or wrong region endpoint
- **Fix:**
  - Double-check AppId and AppSecret from console
  - Ensure system clock is accurate (signatures are time-based)
  - Use the correct regional endpoint

### API: "Device not found" or empty device list
- **Cause:** Camera not bound to the Imou account used for API
- **Fix:** Add camera to Imou Life app with the same account. Ensure device is online.

### Live Stream: HLS URL returns 403 or doesn't play
- **Cause:** URL expired, quota exceeded, or device offline/asleep
- **Fix:**
  - Bind a fresh stream (URLs expire)
  - Check quota in Imou console
  - Wake device first if battery-powered

### Webhook: Not receiving events
- **Cause:** URL not publicly accessible, not HTTPS, or not registered
- **Fix:**
  - Use `ngrok` or similar for local testing
  - Ensure URL is reachable from the internet
  - Verify webhook registration via `getMessageCallback`

---

## General Tips

- **Latency:** Local RTSP is lowest latency. Cloud HLS has 3-10s latency.
- **Bandwidth:** Sub-stream (`subtype=1`) uses ~512kbps. Main stream uses 2-4Mbps.
- **Battery cameras:** They sleep to save power. Cloud snapshot/stream may wake them (takes 3-5s).
- **Security:** Change default passwords. Use VLANs to isolate cameras.
