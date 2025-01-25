from fuzzywuzzy import process
from home_assistant.get_ha_helper import get_ha_services, get_ha_entity_ids
import re


all_services = get_ha_services()
domains = [unit["domain"] for unit in all_services]

def find_number_in_string(text):
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    else:
        return None
    
def find_best_match(input_string, string_list):
    matches = process.extract(input_string, string_list, limit=1)
    if len(matches) > 0:
        return matches[0]

def get_ha_services_for_domain(domain):
    return [key for service in all_services if service["domain"] == domain for key in service["services"].keys()]

def get_command(input_string: str = "turn on ceiling lights color name to blue "):
    services = list(set(service for domain in domains for service in get_ha_services_for_domain(domain)))
    domain_entity_ids = get_ha_entity_ids()

    service = find_best_match(input_string, services)

    entity_ids = [domain_entity_id for domain_entity_id in domain_entity_ids if domain_entity_id.split(".")[0] in domains and service in get_ha_services_for_domain(domain_entity_id.split(".")[0])]
    entity_id = find_best_match(input_string, entity_ids)


    parameters = []
    parameter_value_list = []
    for _service in all_services:
        if _service["domain"] == entity_id.split(".")[0]:
            for __service, value in _service["services"].items():
                if __service == service:
                    for parameter, _value in value["fields"].items():
                        parameters.append(parameter)
                        if _value is not None and _value.get("selector") is not None and _value.get("selector").get("select") is not None and _value.get("selector").get("select").get("options"):
                            for option in _value["selector"]["select"]["options"]:
                                parameter_value_list.append(option)

    parameter = find_best_match(input_string, parameters)
    parameter_value = None
    split_input = input_string.split("to ")
    if len(split_input) > 1:
        if split_input[1]:
            parameter_value = find_best_match(split_input[1], parameter_value_list)

    response = {"service": service, "entity_id": entity_id}
    if parameter is not None and parameter_value is not None:
        response["parameter"] = {"parameter": parameter, "value": parameter_value}
    print(response)
    return response
