import os
import requests_cache

HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HEADERS = {
    "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests_cache.CachedSession("temp/ha_cache", expire_after=86400)


def get_entity_ids(
    entity_type=None, chunk_size=None, chunk_number=None, force_refresh=False
):
    if force_refresh:
        SESSION.cache.clear()

    response = SESSION.get(f"{HOME_ASSISTANT_URL}/states", headers=HEADERS)
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
