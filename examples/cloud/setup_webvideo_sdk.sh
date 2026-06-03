#!/bin/bash
# Setup script: Extract WebVideo SDK files for the browser player example
# Run from the repository root: bash examples/cloud/setup_webvideo_sdk.sh

set -e

SDK_ZIP="imou-webvideo-sdk-demo-for-lightapp.zip"
TARGET_DIR="examples/cloud/webvideo-sdk"

if [ ! -f "$SDK_ZIP" ]; then
  echo "Error: $SDK_ZIP not found in current directory."
  echo "Download it from https://open.imoulife.com or copy the zip to the repo root."
  exit 1
fi

mkdir -p "$TARGET_DIR"
echo "Extracting SDK files to $TARGET_DIR..."

# Extract only the core player files (skip demos to save space)
unzip -o "$SDK_ZIP" \
  "imou-player.js" \
  "imou-player.css" \
  "WasmLib/MultiThread/liblcplay.js" \
  "WasmLib/MultiThread/liblcplay.wasm" \
  "WasmLib/MultiThread/liblcplay.worker.js" \
  "WasmLib/SingleThread/liblcplay.js" \
  "WasmLib/SingleThread/liblcplay.wasm" \
  "WasmLib/SingleThread/PlaySdkWorker.js" \
  "WasmLib/AudioProcessor.js" \
  -d "$TARGET_DIR" 2>/dev/null || {
    # If the zip structure is flat, try alternative extraction
    unzip -o "$SDK_ZIP" -d "$TARGET_DIR"
  }

echo ""
echo "SDK files extracted. To serve the player:"
echo ""
echo "  Option 1 (Node.js):"
echo "    node examples/cloud/webvideo_server.js"
echo ""
echo "  Option 2 (Python):"
echo "    cd examples/cloud/webvideo-sdk && python3 -m http.server 8080"
echo ""
echo "  Then open: http://localhost:8080/../webvideo_player.html"
echo "  (or for Python's http.server, copy webvideo_player.html into webvideo-sdk/)"
echo ""
echo "Get a kitToken first:"
echo "    python examples/cloud/get_kit_token.py"
echo ""
