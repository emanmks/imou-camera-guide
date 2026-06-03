# Browser-Based Streaming via WebVideo SDK

The **Imou WebVideo SDK** (`imou-player.js`) enables browser-based live viewing and
playback using a **WebSocket-based RTSP tunnel** decoded client-side via WebAssembly.
This is different from HLS — it uses the `getKitToken` API to obtain a device-specific
token, then connects directly to the camera via a WebSocket-to-RTSP proxy.

> **Use this when** you need real-time video in a web browser with controls
> (PTZ, snapshot, recording, two-way audio). Not for server-side processing.

---

## How It Works

```
┌──────────────┐    1. AppId+AppSecret     ┌──────────────────┐
│  Your Backend │  ───────────────────────→  │  Imou Open API   │
│  (Python/etc) │  ←── accessToken ────────  │                  │
│               │    2. getKitToken          │                  │
│               │  ───────────────────────→  │                  │
│               │  ←── kitToken ───────────  └──────────────────┘
│               │
│     Serve     │    3. kitToken + deviceId
│    HTML page  │  ───────────────────────→  ┌──────────────────┐
│  (imouPlayer) │                             │  WebSocket RTSP  │
│               │  ←── WebSocket stream ────  │  Proxy Server    │
└──────────────┘                             └──────────────────┘
```

**Key difference from HLS (B4):** HLS is a server-side transcoded stream you
fetch via HTTP and play in a `<video>` tag. The WebVideo SDK is a WebSocket-based
RTSP tunnel that the browser decodes in WASM and renders on a `<canvas>` — lower
latency, H.265 support, two-way audio, and PTZ built-in.

---

## Prerequisites

1. **Imou Open Platform account** with AppId/AppSecret
2. **Device bound** to your Imou account
3. **Video traffic quota** purchased if needed (check console)
4. **WebVideo SDK files** (from `imou-webvideo-sdk-demo-for-lightapp.zip`):

   ```
   imou-player.js           # Core SDK (1.2MB, minified)
   imou-player.css          # Player styles
   WasmLib/MultiThread/     # Multi-thread WASM decoder
   WasmLib/SingleThread/    # Single-thread fallback
   WasmLib/AudioProcessor.js
   ```

---

## Step 1: Get a kitToken (Backend)

The kitToken is a device-specific, time-limited token. Generate it server-side:

```python
# See examples/cloud/get_kit_token.py for full implementation
POST /openapi/getKitToken
{
  "system": {
    "ver": "1.0",
    "appId": "lcxxxxxxxxxxxxxx",
    "sign": "<md5 of time:nonce:appSecret>",
    "time": <unix_ts>,
    "nonce": "<random>"
  },
  "params": {
    "token": "At_...",       # accessToken from auth
    "deviceId": "7H0B18...",
    "channelId": "0",
    "type": 0                 # 0=All, 1=Live, 2=Playback, 6=PTZ
  }
}
```

**Response:**
```json
{
  "result": {
    "code": "0",
    "data": {
      "kitToken": "Kt_hz00e4c3...",
      "expireTime": 7199
    }
  }
}
```

The kitToken is valid for **2 hours**. Cache it server-side for 1 hour.

---

## Step 2: Serve the Browser Player

Include the SDK in your HTML and initialize `imouPlayer`:

```html
<link href="imou-player.css" rel="stylesheet">
<script src="imou-player.js"></script>
<div id="player" style="width:800px;height:500px;"></div>
<script>
const player = new imouPlayer({
  id: "player",
  width: 800,
  height: 500,
  deviceId: "7H0B18XXXXXXXX",
  channelId: "0",
  token: "Kt_hz00e4c3...",       // kitToken from step 1
  type: 1,                         // 1=Live, 2=Playback
  streamId: 0,                     // 0=HD, 1=SD
  recordType: "cloud",             // "cloud" or "localRecord"
  WasmLibPath: "WasmLib/",         // Path to WasmLib directory
  code: "",                        // Video decryption key if set
  muted: false,
  controls: true,
  handleError: (err) => console.error(err),
  handleCallBack: (event) => console.log(event),
});
</script>
```

**Full example:** [`examples/cloud/webvideo_player.html`](../examples/cloud/webvideo_player.html)

---

## Initialization Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | String | Yes | DOM element ID to mount player |
| `width` | Number | Yes | Container width (px) |
| `height` | Number | Yes | Container height (px) |
| `deviceId` | String | Yes | Device serial number (SN) |
| `channelId` | String | Yes | Channel number (typically "0") |
| `token` | String | Yes | kitToken from `getKitToken` API |
| `type` | Number | Yes | `1` = Live, `2` = Playback |
| `streamId` | Number | No | `0` = HD, `1` = SD (default `0`) |
| `recordType` | String | No | `"cloud"` or `"localRecord"` (default `"cloud"`) |
| `code` | String | No | Video decryption key. If device has custom key, use it; if only device password, use password; otherwise use device SN |
| `muted` | Boolean | No | Start muted (default `false`) |
| `controls` | Boolean | No | Show control bar (default `true`) |
| `WasmLibPath` | String | No | Relative/absolute path to WasmLib directory |
| `domain` | String | No | Custom API domain override |
| `dpr` | Number | No | Device pixel ratio (anti-alias, v1.3.0+) |
| `handleError` | Function | No | Error callback |
| `handleCallBack` | Function | No | Event callback (`playStart`, `talkStart`, `talkEnd`) |
| `controlsConfig` | Array | No | Array of control names to show |
| `templateMode` | String | No | `"pc"` or `"mobile"` |

---

## Player Methods

| Method | Description |
|--------|-------------|
| `play()` | Start/resume playback |
| `pause()` | Pause playback |
| `start()` | Resume after pause (reconnect) |
| `destroy()` | End playback and remove DOM |
| `capture()` | Take screenshot (saves as download) |
| `startTalk()` | Start two-way intercom |
| `stopTalk()` | End intercom |
| `volume(0\|1)` | Mute/unmute |
| `fullScreen()` | Enter fullscreen |
| `exitFullScreen()` | Exit fullscreen |
| `startRecord()` | Start screen recording (MP4) |
| `stopRecord()` | Stop recording and download |
| `setSpeed(n)` | Playback speed (0.5, 1, 2, 4, 8, 16, 32) |
| `zoomIn()` / `zoomOut()` / `resetZoom()` | Digital zoom |

---

## Server Requirements

The SDK uses **multi-thread WASM decoding** via `SharedArrayBuffer` by default.
Your server MUST include these headers:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

**Node.js:**
```javascript
response.setHeader("Cross-Origin-Opener-Policy", "same-origin");
response.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
```

**Nginx:**
```nginx
add_header Cross-Origin-Opener-Policy "same-origin";
add_header Cross-Origin-Embedder-Policy "require-corp";
```

Without these headers, the SDK falls back to single-thread mode (slower).

---

## Comparison: HLS vs WebVideo SDK

| Feature | HLS (B4) | WebVideo SDK (B8/B9) |
|---------|----------|---------------------|
| Protocol | HTTP (HLS .m3u8) | WebSocket RTSP tunnel |
| Decoding | Browser native (`<video>`) | WASM software decode (`<canvas>`) |
| Codecs | H.264 only | H.264 + H.265 |
| Latency | 3-10s | 1-3s |
| Two-way audio | ❌ | ✅ |
| PTZ control | ❌ | ✅ Built-in |
| Snapshot | API call | Client-side canvas capture |
| Screen recording | ❌ | ✅ Built-in |
| Browser support | All modern browsers | Chrome/Firefox/Edge >= 55 |
| Dependency | None | imou-player.js + WasmLib (~11MB) |
| Server needed | Any HTTP server | Server with COOP/COEP headers |

---

## Error Codes

| Code | Meaning |
|------|---------|
| 1001 | Decryption failed — re-enter key/code |
| 1002 | Device response exception |
| 2001 | Failed to get intercom address |
| 2002 | Intercom connection failed |
| 2003 | Device does not support intercom |
| 2004-2009 | Intercom errors |

---

## Running the Example

```bash
# 1. Extract SDK files
bash examples/cloud/setup_webvideo_sdk.sh

# 2. Start the server
node examples/cloud/webvideo_server.js

# 3. Get a kitToken (in another terminal)
python examples/cloud/get_kit_token.py

# 4. Open the player
#    http://localhost:8001/webvideo_player.html
#    Paste the kitToken and deviceId, or use URL params:
#    http://localhost:8001/webvideo_player.html?deviceId=7H0B18...&kitToken=Kt_...&domain=openapi-sg.easy4ip.com
```

---

## References

- WebVideo SDK Demo: `imou-webvideo-sdk-demo-for-lightapp.zip` (included)
- Official docs: https://open.imoulife.com/book/en/lightApp/develop.html
- Online demo: https://open.imoulife.com/imou-player/indexEn.html
