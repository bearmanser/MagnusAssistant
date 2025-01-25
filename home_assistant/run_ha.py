import requests
# from dotenv import load_dotenv

from config.config import get_config_value


def run_ha(command):
    api_url = get_config_value("home_assistant.api_url")
    api_key = get_config_value("home_assistant.api_key")
    services_url = f"{api_url}/services/{command['entity_id'].split('.')[0]}/{command['service']}"
    data = {
        "entity_id": command.get('entity_id'),
    }

    if 'parameter' in command:
        data[command["parameter"]["parameter"]] = command["parameter"]["value"]

    response = requests.post(services_url, json=data,
                             headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    print(response)
