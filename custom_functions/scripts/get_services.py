import os
import requests_cache

HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HEADERS = {
    "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests_cache.CachedSession('temp/ha_cache', expire_after=86400)

def get_services(chunk_size=None, chunk_number=None, force_refresh=False):
    """
    Retrieves a list of services from a cached API request.

    Args:
        chunk_size (int, optional): The number of services to retrieve per chunk. Defaults to None.
        chunk_number (int, optional): The chunk number to retrieve. Defaults to None.
        force_refresh (bool, optional): Force fetching fresh data from the API. Defaults to False.
        expire_after (int, optional): Custom expiration time for the request. Defaults to None.

    Returns:
        list: A list of services.
    """
    if force_refresh:
        SESSION.cache.clear()

    response = SESSION.get(f"{HOME_ASSISTANT_URL}/services", headers=HEADERS)
    
    if response.status_code == 200:
        services = response.json()
    else:
        print(f"Error: Unable to fetch services. Status code: {response.status_code}")
        return []
    
    if chunk_size and chunk_number:
        start_index = (chunk_number - 1) * chunk_size
        end_index = start_index + chunk_size
        services = services[start_index:end_index]
    
    return services
