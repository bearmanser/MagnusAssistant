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
        session.cache.clear()

    response = session.get(f"{api_url}/services", headers=headers)
    
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
