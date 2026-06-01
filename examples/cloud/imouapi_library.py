"""
B2. Using `imouapi` Library

Higher-level Python library wrapping the Imou HTTP API.
Provides device and sensor abstractions.

Prerequisites:
    pip install imouapi

Library: https://github.com/user2684/imouapi
Docs: https://user2684.github.io/imouapi
"""

import asyncio
import aiohttp
from imouapi.api import ImouAPIClient
from imouapi.device import ImouDiscoverService, ImouDevice

# ================= CONFIGURATION =================
APP_ID = "YOUR_APP_ID"
APP_SECRET = "YOUR_APP_SECRET"
API_URL = "https://openapi.easy4ip.com/openapi"   # Adjust region if needed
# =================================================


async def main():
    async with aiohttp.ClientSession() as session:
        # Initialize API client
        api_client = ImouAPIClient(APP_ID, APP_SECRET, session)
        api_client.set_base_url(API_URL)

        # Connect (get access token)
        connected = await api_client.async_connect()
        print(f"Connected: {connected}")

        # Discover devices
        discover = ImouDiscoverService(api_client)
        devices = await discover.async_discover_devices()
        print(f"Found {len(devices)} device(s)")

        for dev_info in devices:
            device_id = dev_info.get("deviceId")
            name = dev_info.get("name")
            print(f"\n  Device: {name} ({device_id})")

            # Initialize high-level device object
            device = ImouDevice(api_client, device_id)
            await device.async_initialize()
            print(f"  Status : {device.get_status()}")
            print(f"  Online : {device.is_online()}")
            print(f"  Model  : {device.get_model()}")

            # List sensors / cameras
            for sensor in device.get_all_sensors():
                print(f"  Sensor : {sensor.get_description()} ({sensor.get_name()})")

        await api_client.async_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
