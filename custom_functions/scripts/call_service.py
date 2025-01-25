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





def call_service(domain, service, entity_id, service_data=None):

    """

    Calls a Home Assistant service to control a device or automation.



    Parameters:

    domain (str): The domain of the service, e.g., light, switch, automation.

    service (str): The service to call, e.g., turn_on, turn_off.

    entity_id (str): The ID of the entity to control, e.g., light.living_room.

    service_data (dict, optional): Additional data needed for the service, e.g., brightness, temperature.



    Returns:

    response (dict): Response from the Home Assistant API.

    """



    payload = {"entity_id": entity_id}



    if service_data:

        payload.update(service_data)



    url = f"{api_url}/services/{domain}/{service}"

    response = requests.post(url, headers=headers, json=payload)



    if response.status_code == 200:

        return response.json()

    else:

        print(f"Error: Unable to call service. Status code: {response.status_code}")

        return None

