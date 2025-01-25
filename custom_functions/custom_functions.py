import json


def get_custom_functions():
    custom_functions = []
    with open("custom_functions/function_definitions.json", "r") as f:
        data = json.load(f)
        for function in data:
            custom_functions.append(function)
    return custom_functions
