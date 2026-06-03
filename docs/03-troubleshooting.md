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

### API: "Invalid sign" or "Unauthorized" (SN1001/SN1004)
- **Cause:** Wrong AppSecret, clock skew, or wrong region endpoint
- **Fix:**
  - Double-check AppId and AppSecret from console
  - Ensure system clock is accurate (signatures are time-based)
  - Use the correct regional endpoint for your account
  - Check that `currentDomain` from auth response is being used for subsequent calls

### API: "Token overdue" (TK1002)
- **Cause:** accessToken expired (valid ~72 hours typically)
- **Fix:** Call `accessToken` again to get a fresh token. The SDK handles this automatically.

### API: "Parameter missing" (OP1002)
- **Cause:** Wrong endpoint or missing required parameters
- **Fix:**
  - `deviceBaseList` requires `{"bindId": -1, "limit": 50, "type": "bindAndShare", "needApInfo": true}`
  - `listDeviceDetailsByPage` requires `{"page": 1, "pageSize": 50}`
  - Check API docs for correct parameter names

### API: "Device not found" or empty device list
- **Cause:** Camera not bound to the Imou account used for API
- **Fix:** Add camera to Imou Life app with the same account. Ensure device is online.

### Live Stream: HLS URL returns 403 or doesn't play
- **Cause:** URL expired, quota exceeded, device offline/asleep, or codec mismatch
- **Fix:**
  - Bind a fresh stream via `bindDeviceLive` (URLs expire)
  - First check existing stream via `getLiveStreamInfo`
  - Check quota in Imou console — purchase traffic if needed
  - Wake device first if battery-powered (`wakeUpDevice`)
  - **Codec check:** Cloud live only supports **H.264 video + AAC audio**.
    If playback fails silently, log into the device's local web UI and switch
    from H.265/H.265+ to H.264, and audio to AAC.

### Live Stream: "The video live exists" (LV1001)
- **Cause:** A live stream is already bound for this device/channel
- **Fix:** Query existing stream via `getLiveStreamInfo` instead of trying to bind again. Don't create multiple streams.

### Live Stream: "The video live does not exist" (LV1002)
- **Cause:** No active stream
- **Fix:** Call `bindDeviceLive` to create a new stream.

### Snapshot: No URL returned
- **Cause:** Wrong endpoint or device offline
- **Fix:** Use `setDeviceSnapEnhanced` (NOT `deviceSnap` which is deprecated).
  Wait 3-5 seconds before downloading the returned URL.

### Webhook: Not receiving events
- **Cause:** URL not publicly accessible, not HTTPS, or not registered
- **Fix:**
  - Use `ngrok` or similar for local testing
  - Ensure URL is reachable from the internet
  - Verify webhook registration includes `callbackFlag` and `status` params

### WebVideo SDK Player: WasmLib loading failure
- **Cause:** WasmLib files not found or wrong path
- **Fix:** Set `WasmLibPath` correctly. The WasmLib directory must contain
  `liblcplay.wasm`, `liblcplay.js`, and worker files. Download fresh SDK files
  if corrupt.

### WebVideo SDK Player: 404 on WebSocket connection
- **Cause:** kitToken expired or wrong domain
- **Fix:** Generate a fresh kitToken via `getKitToken` API (valid 2 hours).
  Don't request the stream URL too early — call the API only when needed.

### WebVideo SDK: COOP/COEP headers missing
- **Cause:** Server must send `Cross-Origin-Opener-Policy` and
  `Cross-Origin-Embedder-Policy` headers for multi-thread WASM mode
- **Fix:** Add the headers to your server config (see `docs/06-browser-streaming.md`).
  Without them, it falls back to single-thread mode (slower).

### API: "Request failed" — general
- **Cause:** Network issue or server error
- **Fix:**
  - Check network connectivity and firewall
  - Verify the API URL format: `https://{domain}/openapi/{endpoint}`
  - Ensure `Content-Type: application/json` header is set

---

## General Tips

- **Latency:** Local RTSP is lowest latency. Cloud HLS has 3-10s latency.
  WebVideo SDK (WebSocket RTSP) is ~1-3s.
- **Bandwidth:** Sub-stream (`subtype=1`) uses ~512kbps. Main stream uses 2-4Mbps.
- **Battery cameras:** They sleep to save power. Cloud snapshot/stream may wake
  them (takes 3-5s). Use `wakeUpDevice` API for battery-powered devices.
- **Security:** Change default passwords. Use VLANs to isolate cameras.
- **SDK patterns:** The pyimouapi SDK (v1.2.7) is the reference implementation.
  Source at https://github.com/Imou-OpenPlatform/Py-Imou-Open-Api .
