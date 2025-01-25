import json


def get_config_value(keys_str):
    try:
        keys = keys_str.split(".")
        with open("config/config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        value = data
        for key in keys:
            value = value[key]
        return value
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return None
