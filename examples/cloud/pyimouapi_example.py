"""
B3. Using Official `pyimouapi` Library

The official Python library maintained by Imou Open Platform,
used by the Home Assistant integration.

Prerequisites:
    pip install pyimouapi

GitHub: https://github.com/Imou-OpenPlatform/Imou-Home-Assistant
"""

import asyncio
import aiohttp
from pyimouapi.api import ImouAPIClient
from pyimouapi.device import ImouDiscoverService

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
API_URL = "https://openapi.easy4ip.com/openapi"
# =================================================


async def main():
    async with aiohttp.ClientSession() as session:
        client = ImouAPIClient(APP_ID, APP_SECRET, session)
        client.set_base_url(API_URL)

        print("Connecting to Imou cloud...")
        await client.async_connect()
        print("Authenticated successfully\n")

        discover = ImouDiscoverService(client)
        devices = await discover.async_discover_devices()
        print(f"Discovered {len(devices)} device(s)\n")

        for dev in devices:
            print(f"  Name      : {dev.get('name')}")
            print(f"  Device ID : {dev.get('deviceId')}")
            print(f"  Model     : {dev.get('deviceModel')}")
            print(f"  Status    : {dev.get('status')}")
            print()

        await client.async_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
