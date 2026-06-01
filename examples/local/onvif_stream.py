"""
A5. ONVIF Stream URI

Use ONVIF protocol to query the camera for its official RTSP stream URI.
This is more reliable than guessing the RTSP URL format.

Prerequisites:
    pip install onvif-zeep

Note: ONVIF must be enabled on the camera.
"""

from onvif import ONVIFCamera

# ================= CONFIGURATION =================
CAMERA_IP = "192.168.1.100"
ONVIF_PORT = 80                    # Often 80, 8080, or 2020
USER = "admin"
PASSWORD = "YOUR_SAFETY_CODE"
# =================================================


def get_stream_uri(profile_name: str = None):
    """Connect via ONVIF and get the RTSP stream URI."""
    print(f"Connecting to ONVIF camera at {CAMERA_IP}:{ONVIF_PORT}")
    camera = ONVIFCamera(CAMERA_IP, ONVIF_PORT, USER, PASSWORD)

    # Create media service
    media = camera.create_media_service()

    # Get available profiles (stream configs)
    profiles = media.GetProfiles()
    print(f"Found {len(profiles)} profile(s)")

    for idx, profile in enumerate(profiles):
        pname = profile.Name
        token = profile.token
        print(f"  [{idx}] Profile: {pname} (token={token})")

        # Get stream URI for this profile
        stream_setup = {
            "StreamSetup": {
                "Stream": "RTP-Unicast",     # or RTP_Multicast
                "Transport": {"Protocol": "RTSP"},
            },
            "ProfileToken": token,
        }
        uri = media.GetStreamUri(stream_setup)
        print(f"      RTSP URI: {uri.Uri}")
        print()

    # Optionally return the first profile's URI
    if profiles:
        first = profiles[0]
        stream_setup = {
            "StreamSetup": {
                "Stream": "RTP-Unicast",
                "Transport": {"Protocol": "RTSP"},
            },
            "ProfileToken": first.token,
        }
        uri = media.GetStreamUri(stream_setup)
        return uri.Uri
    return None


def main():
    uri = get_stream_uri()
    if uri:
        print(f"Recommended stream URI:\n  {uri}")
    else:
        print("Failed to retrieve stream URI")


if __name__ == "__main__":
    main()
