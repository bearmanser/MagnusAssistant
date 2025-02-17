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
        session.cache.clear()
    
    # Make the request to get the entity state
    url = f"{api_url}/states/{entity_id}"
    response = session.get(url, headers=headers, expire_after=60)

    # Check the response status
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to get entity state. Status code: {response.status_code}")
        return None
