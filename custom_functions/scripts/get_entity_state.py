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







def get_entity_state(entity_id):

    """

    Gets the current state of a specific entity in Home Assistant.



    Parameters:

    entity_id (str): The ID of the entity, e.g., light.living_room.



    Returns:

    state (dict): The current state of the entity if successful, otherwise None.

    """



    # Make the request to get the entity state

    url = f"{api_url}/states/{entity_id}"

    response = requests.get(url, headers=headers)



    # Check the response status

    if response.status_code == 200:

        return response.json()

    else:

        print(f"Error: Unable to get entity state. Status code: {response.status_code}")

        return None

