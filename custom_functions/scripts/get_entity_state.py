import os
import requests_cache

HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HEADERS = {
    "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests_cache.CachedSession('temp/ha_cache', expire_after=86400)

def get_entity_state(entity_id, force_refresh=False):
    """
    Gets the current state of a specific entity in Home Assistant.

    Parameters:
    entity_id (str): The ID of the entity, e.g., light.living_room.
    force_refresh (bool, optional): Whether to force a fresh request. Defaults to False.
    expire_after (int, optional): Custom expiration time for the request. Defaults to None.

    Returns:
    state (dict): The current state of the entity if successful, otherwise None.
    """
    if force_refresh:
        SESSION.cache.clear()
    
    # Make the request to get the entity state
    url = f"{HOME_ASSISTANT_URL}/states/{entity_id}"
    response = SESSION.get(url, headers=HEADERS, expire_after=60)

    # Check the response status
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to get entity state. Status code: {response.status_code}")
        return None
