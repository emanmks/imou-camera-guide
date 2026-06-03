/**
 * B9 (Server). Node.js HTTP server for the WebVideo SDK player demo.
 *
 * Serves the WebVideo SDK files with the required COOP/COEP headers
 * for SharedArrayBuffer (multi-thread WASM decoding).
 *
 * Usage:
 *   1. Run setup: bash examples/cloud/setup_webvideo_sdk.sh
 *   2. Start:    node examples/cloud/webvideo_server.js
 *   3. Get a kitToken: python examples/cloud/get_kit_token.py
 *   4. Open:    http://localhost:8001/webvideo_player.html
 *
 * Based on the official node-demo from imou-webvideo-sdk-demo-for-lightapp.
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 8001;

// MIME types
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js":   "application/javascript",
  ".css":  "text/css",
  ".wasm": "application/wasm",
  ".json": "application/json",
  ".png":  "image/png",
  ".jpg":  "image/jpeg",
  ".svg":  "image/svg+xml",
};

const SDK_DIR = path.join(__dirname, "webvideo-sdk");

const server = http.createServer((req, res) => {
  // Resolve path — serve from SDK_DIR for SDK files, or from examples/cloud for .html
  let filePath;
  if (req.url.startsWith("/WasmLib/") || req.url === "/imou-player.js" || req.url === "/imou-player.css") {
    filePath = path.join(SDK_DIR, req.url);
  } else {
    filePath = path.join(__dirname, req.url === "/" ? "webvideo_player.html" : req.url);
  }

  const ext = path.extname(filePath);

  // COOP/COEP headers required for SharedArrayBuffer multi-thread WASM
  res.setHeader("Cross-Origin-Opener-Policy", "same-origin");
  res.setHeader("Cross-Origin-Embedder-Policy", "require-corp");
  res.setHeader("Access-Control-Allow-Origin", "*");

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("404 Not Found: " + req.url);
      return;
    }
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`Imou WebVideo SDK server running:`);
  console.log(`  http://localhost:${PORT}/webvideo_player.html`);
  console.log(`\nGet a kitToken first:`);
  console.log(`  python examples/cloud/get_kit_token.py`);
  console.log(`\nThen set the parameters in the browser or pass as URL query:`);
  console.log(`  http://localhost:${PORT}/webvideo_player.html?deviceId=XXX&kitToken=Kt_...&domain=openapi-sg.easy4ip.com`);
});
