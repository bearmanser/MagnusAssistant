import os
import requests_cache

api_key = os.getenv("HOME_ASSISTANT_TOKEN")
api_url = os.getenv("HOME_ASSISTANT_URL")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Setup cache with a 24-hour expiration
session = requests_cache.CachedSession('ha_cache', expire_after=86400)

def call_service(domain, service, entity_id, service_data=None, force_refresh=False):
    """
    Calls a Home Assistant service to control a device or automation.

    Parameters:
    domain (str): The domain of the service, e.g., light, switch, automation.
    service (str): The service to call, e.g., turn_on, turn_off.
    entity_id (str): The ID of the entity to control, e.g., light.living_room.
    service_data (dict, optional): Additional data needed for the service, e.g., brightness, temperature.
    force_refresh (bool, optional): Whether to force a fresh request. Defaults to False.
    expire_after (int, optional): Custom expiration time for the request. Defaults to None.

    Returns:
    response (dict): Response from the Home Assistant API.
    """
    if force_refresh:
        session.cache.clear()
    
    payload = {"entity_id": entity_id}
    
    if service_data:
        payload.update(service_data)
    
    url = f"{api_url}/services/{domain}/{service}"
    response = session.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to call service. Status code: {response.status_code}")
        return None