import os
import json
import requests

hass_token = os.getenv('HASS_TOKEN')
hass_url = os.getenv('HASS_URL')

headers = {
    "Authorization": f"Bearer {hass_token}",
    "Content-Type": "application/json"
}

included_device_classes = os.getenv('INCLUDED_DEVICE_CLASSES', 'light,switch,climate,cover,media_player,fan,lock').split(',')

def list_devices():
    """List actual devices, excluding specified device classes."""
    # Get the areas
    response = requests.get(f"{hass_url}/states", headers=headers)
    devices = []
    for entity in response.json():
        # Skip entities with device_class firmware
        try:
            if not any(entity['entity_id'].startswith(device_class) for device_class in included_device_classes):
                continue
        except KeyError:
            pass
        # Get the area_id from the entity and map it to an area name
        print(entity)
        print("-------")
        # devices.append({
        #     entity['entity_id']: {
        #         "state": entity['state'],
        #         "location": location
        #     }
        # })
    return devices

homeassistant_tool = [list_devices,]

if __name__ == "__main__":
    for device in list_devices():
        print(device)

