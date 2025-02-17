import os
import requests_cache

HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HEADERS = {
    "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests_cache.CachedSession('temp/ha_cache', expire_after=86400)

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
        SESSION.cache.clear()
    
    payload = {"entity_id": entity_id}
    
    if service_data:
        payload.update(service_data)
    
    url = f"{HOME_ASSISTANT_URL}/services/{domain}/{service}"
    response = SESSION.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to call service. Status code: {response.status_code}")
        return None