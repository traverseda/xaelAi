import os
import json
import requests

hass_token = os.getenv('HASS_TOKEN')
hass_url = os.getenv('HASS_URL')

headers = {
    "Authorization": f"Bearer {hass_token}",
    "Content-Type": "application/json"
}

included_device_classes = os.getenv('INCLUDED_DEVICE_CLASSES', 'light,switch,climate,cover,media_player,fan,lock,scene').split(',')

def get_areas():
    """Retrieve the list of areas using the template API."""
    template_payload = {"template": "{{ areas() }}"}
    response = requests.post(f"{hass_url}/api/template", headers=headers, json=template_payload)
    return response.json()

print(get_areas())


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
        friendly_name = entity.get('attributes', {}).get('friendly_name', 'Unknown')
        state = entity.get('state', 'Unknown')
        entity_type = entity['entity_id'].split('.')[0]
        devices.append({
            'entity_type': entity_type,
            'friendly_name': friendly_name,
            'state': state
        })
    return devices

homeassistant_tool = [list_devices,]

if __name__ == "__main__":
    for device in list_devices():
        print(device)

