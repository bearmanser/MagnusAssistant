import os
import requests_cache

api_key = os.getenv("HOME_ASSISTANT_TOKEN")
api_url = os.getenv("HOME_ASSISTANT_URL")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Setup cache with a 24-hour expiration
session = requests_cache.CachedSession("ha_cache", expire_after=86400)


def get_entity_ids(
    entity_type=None, chunk_size=None, chunk_number=None, force_refresh=False
):
    if force_refresh:
        session.cache.clear()

    response = session.get(f"{api_url}/states", headers=headers)
    if response.status_code == 200:
        entity_ids = response.json()
    else:
        print(f"Error: Unable to fetch states. Status code: {response.status_code}")
        return []

    if entity_type:
        entity_ids = [
            entity
            for entity in entity_ids
            if entity["entity_id"].startswith(entity_type)
        ]

    if chunk_size and chunk_number:
        start_index = (chunk_number - 1) * chunk_size
        end_index = start_index + chunk_size
        entity_ids = entity_ids[start_index:end_index]

    return [
        {
            "friendly_name": entity.get("attributes", {}).get("friendly_name", ""),
            "entity_id": entity["entity_id"],
        }
        for entity in entity_ids
    ]
