"""
A6. HTTP Snapshot (JPEG)

Grab a single JPEG snapshot via HTTP instead of maintaining a continuous RTSP stream.
Useful for periodic capture, thumbnails, or when bandwidth is limited.

Prerequisites:
    pip install requests

Note: This endpoint is commonly available on Dahua/Imou firmware.
If it returns 401, you may need to use digest authentication.
"""

import requests
from requests.auth import HTTPDigestAuth

# ================= CONFIGURATION =================
CAMERA_IP = "192.168.1.100"
USER = "admin"
PASSWORD = "YOUR_SAFETY_CODE"
OUTPUT_FILE = "http_snapshot.jpg"
# =================================================

SNAPSHOT_URL = f"http://{CAMERA_IP}/cgi-bin/snapshot.cgi"


def get_snapshot():
    """Fetch JPEG snapshot from camera."""
    print(f"Fetching snapshot from {SNAPSHOT_URL}")

    try:
        # Try basic auth first
        resp = requests.get(SNAPSHOT_URL, auth=(USER, PASSWORD), timeout=10)

        # If 401, try digest auth
        if resp.status_code == 401:
            print("Basic auth failed, trying digest auth...")
            resp = requests.get(
                SNAPSHOT_URL,
                auth=HTTPDigestAuth(USER, PASSWORD),
                timeout=10,
            )

        if resp.status_code == 200:
            with open(OUTPUT_FILE, "wb") as f:
                f.write(resp.content)
            print(f"Snapshot saved to {OUTPUT_FILE} ({len(resp.content)} bytes)")
        else:
            print(f"Failed: HTTP {resp.status_code}")
            print(f"Response: {resp.text[:200]}")

    except requests.exceptions.ConnectionError:
        print(f"Connection error. Is {CAMERA_IP} reachable?")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    get_snapshot()
