from home_assistant.get_ha_helper import get_ha_entity_ids, get_ha_services, post_ha_conversation
from .fuzzy_matching_algorithm import find_best_match


def intent_recognition(input_string: str = "turn off ikke trykk her"):
    services_data = get_ha_services()
    entity_data = get_ha_entity_ids()
    entity_names = [entry["attributes"]["friendly_name"] if "attributes" in entry and "friendly_name" in entry[
        "attributes"] else None for entry in entity_data]
    entity_name, entity_name_score = find_best_match(input_string, entity_names)
    if entity_name_score < 75:
        raise

    for entry in entity_data:
        if "attributes" in entry and "friendly_name" in entry["attributes"]:
            if entry["attributes"]["friendly_name"] == entity_name:
                entity_id = entry["entity_id"]
                break

    alternate_keywords = ["set"]
    words = input_string.split()
    options = []
    for word in words:
        if find_best_match(word, alternate_keywords)[1] > 90:
            if find_best_match("to", words)[1] > 90:
                for item in services_data:
                    if item["domain"] == entity_id.split(".")[0]:
                        for service in item["services"].values():
                            for field in service["fields"].values():
                                if "selector" in field and "select" in field["selector"] and "options" in \
                                        field["selector"]["select"]:
                                    for option in field["selector"]["select"]["options"]:
                                        options.append(option)
    option_name = None
    service = None
    if len(options) > 0 and "to" in words:
        option, option_score = find_best_match(input_string.split("to")[1], options)
        if option_score > 90:
            for word in words:
                if find_best_match(word, alternate_keywords)[1] > 90:
                    for item in services_data:
                        if item["domain"] == entity_id.split(".")[0]:
                            for _service_key, _service in item["services"].items():
                                for field_name, field in _service["fields"].items():
                                    if "selector" in field and "select" in field["selector"] and "options" in \
                                            field["selector"]["select"]:
                                        for _option in field["selector"]["select"]["options"]:
                                            if _option == option and option_name is None:
                                                service = _service_key
                                                option_name = field_name

    if service is None:
        services = None
        for item in services_data:
            if item["domain"] == entity_id.split(".")[0]:
                services = item["services"].keys()
        service, service_score = find_best_match(input_string, services)
        if service_score < 75:
            raise

    if option_name is None:
        print(service, entity_id)
    else:
        print(service, entity_id, option_name, option)

    response = {"service": service, "entity_id": entity_id}
    if option_name is not None and option is not None:
        response["parameter"] = {"parameter": option_name, "value": option}
    return response
