"""
A2. RTSP via OpenCV

Capture frame-by-frame from Imou camera RTSP stream using OpenCV.
Ideal for computer vision, motion detection, AI processing.

Prerequisites:
    pip install opencv-python
"""

import cv2
import sys

# ================= CONFIGURATION =================
CAMERA_IP = "192.168.1.100"
PASSWORD = "YOUR_SAFETY_CODE"
CHANNEL = 1
SUBTYPE = 0                          # 0=HD, 1=SD
# =================================================

RTSP_URL = (
    f"rtsp://admin:{PASSWORD}@{CAMERA_IP}/cam/realmonitor"
    f"?channel={CHANNEL}&subtype={SUBTYPE}&unicast=true&proto=Onvif"
)


def capture_frames():
    """Open RTSP stream and display frames."""
    # OpenCV VideoCapture with reduced buffer for lower latency
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"ERROR: Cannot open stream at {RTSP_URL}")
        sys.exit(1)

    print("Stream opened. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read failed. Retrying...")
            continue

        # Example: add text overlay
        cv2.putText(
            frame,
            "Imou Camera - Local RTSP",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Imou Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def save_snapshot(output_path: str = "snapshot.jpg"):
    """Grab a single frame and save as JPEG."""
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("ERROR: Cannot open stream")
        return

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Snapshot saved to {output_path}")
    else:
        print("Failed to grab frame")

    cap.release()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["display", "snapshot"], default="display")
    args = parser.parse_args()

    if args.action == "display":
        capture_frames()
    else:
        save_snapshot()
