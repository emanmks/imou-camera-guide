"""
A1. Direct RTSP Stream

Capture or record RTSP stream using ffmpeg subprocess.
This is the simplest method for direct IP access on local network.

Prerequisites:
    - Camera IP address
    - Camera password / safety code
    - ffmpeg installed on your system

RTSP URL Format:
    rtsp://admin:<PASSWORD>@<CAMERA_IP>/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif

    subtype=0  -> Main stream (HD)
    subtype=1  -> Sub stream (SD)
"""

import subprocess
import sys

# ================= CONFIGURATION =================
CAMERA_IP = "192.168.1.100"          # Your camera's local IP
PASSWORD = "YOUR_SAFETY_CODE"        # From camera sticker or your changed password
CHANNEL = 1                          # Camera channel (1 for direct camera)
SUBTYPE = 0                          # 0=HD, 1=SD
OUTPUT_FILE = "capture.mp4"          # Output file or "-" for stdout
# =================================================

RTSP_URL = (
    f"rtsp://admin:{PASSWORD}@{CAMERA_IP}/cam/realmonitor"
    f"?channel={CHANNEL}&subtype={SUBTYPE}&unicast=true&proto=Onvif"
)


def capture_stream(duration_sec: int = 30):
    """Capture stream to file for a given duration."""
    cmd = [
        "ffmpeg",
        "-y",                       # Overwrite output
        "-i", RTSP_URL,             # Input RTSP
        "-t", str(duration_sec),    # Duration
        "-c", "copy",               # Copy without re-encoding
        OUTPUT_FILE,
    ]
    print(f"Capturing {duration_sec}s from {RTSP_URL}")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Saved to {OUTPUT_FILE}")


def play_stream():
    """Play stream using ffplay (opens a window)."""
    cmd = ["ffplay", "-fflags", "nobuffer", "-flags", "low_delay", RTSP_URL]
    print(f"Playing {RTSP_URL}")
    subprocess.run(cmd)


def stream_to_stdout():
    """Output raw H264 to stdout for piping to other tools."""
    cmd = [
        "ffmpeg",
        "-i", RTSP_URL,
        "-c", "copy",
        "-f", "h264",
        "-",
    ]
    print(f"Streaming raw H264 to stdout...")
    subprocess.run(cmd)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Direct RTSP capture from Imou camera")
    parser.add_argument("action", choices=["capture", "play", "stdout"], default="play")
    parser.add_argument("--duration", type=int, default=30, help="Capture duration in seconds")
    args = parser.parse_args()

    if args.action == "capture":
        capture_stream(args.duration)
    elif args.action == "play":
        play_stream()
    elif args.action == "stdout":
        stream_to_stdout()
