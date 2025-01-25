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


def get_ha_entity_ids():
    file_path = os.path.join(data_folder, "entity_ids.json")

    if os.path.exists(file_path):
        modified_time = os.path.getmtime(file_path)
        modified_date = datetime.fromtimestamp(modified_time).date()
        current_date = datetime.now().date()

        if modified_date == current_date:
            with open(file_path, "r") as file:
                entity_ids = json.load(file)
            return entity_ids

    response = requests.get(f"{api_url}/states", headers=headers)

    if response.status_code == 200:
        with open(file_path, "w") as file:
            json.dump(response.json(), file)
        return response.json()
    else:
        print(f"Error: Unable to fetch states. Status code: {response.status_code}")
        return []


def get_ha_services():
    file_path = os.path.join(data_folder, "services.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            services = json.load(file)
        return services
    else:
        response = requests.get(f"{api_url}/services", headers=headers)
        if response.status_code == 200:
            with open(file_path, "w") as file:
                json.dump(response.json(), file)
            return response.json()
        else:
            print(f"Error: Unable to fetch services. Status code: {response.status_code}")
            return []


def post_ha_conversation(text):
    json_data = {
          "text": text,
          "language": "en"
        }
    response = requests.post(f"{api_url}/conversation/process", headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch services. Status code: {response.status_code}")
        return False
