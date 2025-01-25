import json

import os

from datetime import datetime

import requests

from config.config import get_config_value



api_key = get_config_value("home_assistant.api_key")

api_url = get_config_value("home_assistant.api_url")

data_folder = "ha_data"

headers = {

    "Authorization": f"Bearer {api_key}",

    "Content-Type": "application/json",

}





def get_entity_ids(

    entity_type=None, chunk_size=None, chunk_number=None, force_refresh=False

):

    file_path = os.path.join(data_folder, "entity_ids.json")



    if not force_refresh and os.path.exists(file_path):

        modified_time = os.path.getmtime(file_path)

        modified_date = datetime.fromtimestamp(modified_time).date()

        current_date = datetime.now().date()



        if modified_date == current_date:

            with open(file_path, "r") as file:

                entity_ids = json.load(file)

            return [

                {

                    "friendly_name": entity.get("attributes", {}).get(

                        "friendly_name", ""

                    ),

                    "entity_id": entity["entity_id"],

                }

                for entity in entity_ids

            ]



    response = requests.get(f"{api_url}/states", headers=headers)

    if response.status_code == 200:

        entity_ids = response.json()

        with open(file_path, "w") as file:

            json.dump(entity_ids, file)

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



