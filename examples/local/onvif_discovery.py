"""
A4. ONVIF Discovery

Automatically discover ONVIF-compatible cameras on the local network
without knowing their IP addresses beforehand.

Prerequisites:
    pip install onvif-zeep

Note: Some Imou cameras ship with ONVIF disabled by default.
Enable it in the camera settings via the Imou Life app or web UI.
"""

from onvif.client import ONVIFService
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from wsdiscovery.scope import Scope


def discover_onvif_devices(timeout: int = 5):
    """
    Discover ONVIF devices on the local network using WS-Discovery.
    Returns list of discovered device information dicts.
    """
    wsd = WSDiscovery()
    wsd.start()

    # Search for devices in the ONVIF scope
    scopes = [Scope("onvif://www.onvif.org")]
    services = wsd.searchServices(scopes=scopes, timeout=timeout)

    devices = []
    for service in services:
        xaddrs = service.getXAddrs()
        ep_addr = service.getEPR()
        devices.append({
            "epr": ep_addr,
            "xaddrs": xaddrs,
            "ip": xaddrs[0] if xaddrs else None,
        })

    wsd.stop()
    return devices


def main():
    print("Scanning local network for ONVIF devices...")
    found = discover_onvif_devices(timeout=5)

    if not found:
        print("No ONVIF devices found.")
        print("Tip: Ensure ONVIF is enabled in camera settings.")
        return

    print(f"Found {len(found)} device(s):\n")
    for idx, dev in enumerate(found, 1):
        print(f"  [{idx}] IP/URL: {dev['ip']}")
        print(f"       EPR: {dev['epr']}")
        print()


if __name__ == "__main__":
    main()
