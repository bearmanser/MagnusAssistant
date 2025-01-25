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





def get_services(chunk_size=None, chunk_number=None, force_refresh=False):

    """

    Retrieves a list of services from either a local file or an API endpoint.



    Args:

        chunk_size (int, optional): The number of services to retrieve per chunk. Defaults to None.

        chunk_number (int, optional): The chunk number to retrieve. Defaults to None.

        force_refresh (bool, optional): Force fetching fresh data from the API. Defaults to False.



    Returns:

        list: A list of services.

    """

    file_path = os.path.join(data_folder, "services.json")



    if not force_refresh and os.path.exists(file_path):

        with open(file_path, "r") as file:

            services = json.load(file)

        return services  # Return early if data exists and no force refresh



    response = requests.get(f"{api_url}/services", headers=headers)

    if response.status_code == 200:

        services = response.json()

        with open(file_path, "w") as file:

            json.dump(services, file)

    else:

        print(f"Error: Unable to fetch services. Status code: {response.status_code}")

        return []



    if chunk_size and chunk_number:

        start_index = (chunk_number - 1) * chunk_size

        end_index = start_index + chunk_size

        services = services[start_index:end_index]



    return services





