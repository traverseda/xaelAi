import os
import json
import requests

hass_token = os.getenv('HASS_TOKEN')
hass_url = os.getenv('HASS_URL')

headers = {
    "Authorization": f"Bearer {hass_token}",
    "Content-Type": "application/json"
}

def list_devices():
    # Get the areas
    response = requests.get(f"{hass_url}/states", headers=headers)
    devices = []
    for entity in response.json():
        # Skip entities with device_class firmware
        try:
            if entity['attributes']['device_class'] in {'firmware'}:
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

