"""
A7. LAN Network Scanner

Scan your local subnet for cameras with open RTSP port (554)
and optionally test authentication.

Prerequisites:
    - nmap installed on your system (apt install nmap)
    - pip install python-nmap opencv-python

Warning: Only run on networks you own or have permission to scan.
"""

import nmap
import cv2
import sys

# ================= CONFIGURATION =================
SUBNET = "192.168.1.0/24"          # Your local subnet
PASSWORD = "YOUR_SAFETY_CODE"      # Camera password to test
TIMEOUT_MS = 3000                  # RTSP connection timeout
# =================================================


def scan_for_rtsp_hosts(subnet: str) -> list:
    """Scan subnet for hosts with port 554 open."""
    print(f"Scanning {subnet} for RTSP port (554)...")
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments="-p 554 --open -T4")

    hosts = []
    for host in nm.all_hosts():
        if nm[host].has_tcp(554) and nm[host]["tcp"][554]["state"] == "open":
            hosts.append(host)
            print(f"  [OPEN] {host}:554")

    print(f"Found {len(hosts)} host(s) with port 554 open")
    return hosts


def test_rtsp_auth(ip: str, password: str) -> bool:
    """Try to open RTSP stream from IP with given password."""
    url = (
        f"rtsp://admin:{password}@{ip}/cam/realmonitor"
        f"?channel=1&subtype=0&unicast=true&proto=Onvif"
    )
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Try to read a frame with timeout consideration
    # Note: OpenCV read doesn't support direct timeout, so we check quickly
    ret, _ = cap.read()
    cap.release()
    return ret


def main():
    hosts = scan_for_rtsp_hosts(SUBNET)
    if not hosts:
        print("No RTSP hosts found.")
        return

    print("\nTesting authentication on discovered hosts...")
    for ip in hosts:
        print(f"  Testing {ip} ... ", end="", flush=True)
        if test_rtsp_auth(ip, PASSWORD):
            print("SUCCESS")
            # Save working URL info
            print(f"    -> rtsp://admin:***@{ip}/cam/realmonitor?channel=1&subtype=0")
        else:
            print("FAILED (wrong password, not Imou, or unreachable)")


if __name__ == "__main__":
    main()
