import json
import os
import subprocess
from typing import get_args
import requests
from flask import Flask, request
from flask_cors import CORS
from flask_sslify import SSLify
import openai

from twilio_socket.twilio import AUDIO_FOLDER

app = Flask(__name__)
sslify = SSLify(app)
CORS(app, origins=["*"])

path_to_voices_json = "config/piper_files/voices.json"
path_to_config_json = "config/config.json"
url_to_voices = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/voices.json?download=true"
url_to_voice_files = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/{path_to_voice_files}?download=true"


@app.route("/save_assistant", methods=["POST"])
def save_assistant():
    assistant_data = json.loads(request.form["assistant_data"])

    with open(path_to_config_json, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    for id in assistant_data.keys():
        config_data["assistants"][id] = assistant_data[id]

        index = 0
        while True:
            file_key = f"{id}_wakeWordFile_{index}"
            wake_word_file = request.files.get(file_key)

            if wake_word_file:
                save_directory = f"config/wake_word_files/{id}"
                os.makedirs(save_directory, exist_ok=True)
                save_path = f"{save_directory}/{wake_word_file.filename}"
                wake_word_file.save(save_path)
            else:
                break
            index += 1

        voice_key_from_config = assistant_data[id]["voice"]
        if voice_key_from_config is not None:
            with open(path_to_voices_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                files = data[voice_key_from_config]["files"]

            name_key = {"onnx": 0, "onnx.json": 1}

            for extension, index in name_key.items():
                url = url_to_voice_files.replace(
                    "{path_to_voice_files}", list(files.keys())[index]
                )
                response = requests.get(url)
                if response.status_code == 200:
                    folder_path = f"config/piper_files/{voice_key_from_config}"
                    os.makedirs(folder_path, exist_ok=True)
                    with open(
                        f"{folder_path}/{voice_key_from_config}.{extension}", "wb"
                    ) as f:
                        f.write(response.content)

    with open(path_to_config_json, "w") as f:
        json.dump(config_data, f, indent=4)

    return {"message": "Assistant saved successfully"}


@app.route("/delete_assistant", methods=["DELETE"])
def delete_assistant():
    assistant_id = request.get_data(as_text=True)

    with open(path_to_config_json, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    if assistant_id in config_data["assistants"]:
        del config_data["assistants"][assistant_id]

        wake_word_directory = f"config/wake_word_files/{assistant_id}"
        if os.path.exists(wake_word_directory):
            for file in os.listdir(wake_word_directory):
                os.remove(os.path.join(wake_word_directory, file))
            os.rmdir(wake_word_directory)

        with open(path_to_config_json, "w") as f:
            json.dump(config_data, f, indent=4)

        return {"message": "Assistant deleted successfully"}, 200
    else:
        return {"message": "Assistant not found"}, 404


@app.route("/config", methods=["POST"])
def save_config():
    new_config_data = request.get_json().get("config")

    with open(path_to_config_json, "r", encoding="utf-8") as f:
        config = json.load(f)

    config.update(new_config_data)

    with open(path_to_config_json, "w") as f:
        json.dump(config, f, indent=4)

    if os.path.exists(os.path.join(AUDIO_FOLDER, "greeting.wav")):
        os.remove(os.path.join(AUDIO_FOLDER, "greeting.wav"))

    return {"message": "Configuration saved successfully"}


@app.route("/config", methods=["GET"])
def get_config():
    try:
        with open(path_to_config_json, "r", encoding="utf-8") as f:
            config_data = f.read()
        return config_data

    except FileNotFoundError:
        return {"message": "Configuration file not found"}


@app.route("/get_voices", methods=["GET"])
def get_voices():
    try:
        with open(path_to_voices_json, "r", encoding="utf-8") as f:
            config_data = f.read()
        return config_data

    except FileNotFoundError:
        try:
            response = requests.get(url_to_voices)
            with open(path_to_voices_json, "wb") as f:
                f.write(response.content)
            return response.content

        except FileNotFoundError:
            return {"message": "Could not download voice file"}


@app.route("/get_custom_commands", methods=["GET"])
def get_custom_commands():
    with open("custom_functions/function_definitions.json", "r", encoding="utf-8") as f:
        function_definitions = json.load(f)

    for id, function in enumerate(function_definitions):
        _ = {"function_definition": function}

        if os.path.exists(f"custom_functions/scripts/{function['name']}.py"):
            with open(f"custom_functions/scripts/{function['name']}.py", "r", encoding="utf-8") as f:
                _["python_code"] = f.read()
        else:
            _["python_code"] = ""

        function_definitions[id] = _

    return function_definitions


@app.route("/custom_command", methods=["POST"])
def custom_command():
    data = request.get_json()
    function_definitions = []

    with open("custom_functions/function_definitions.json", "r", encoding="utf-8") as f:
        function_definitions = json.load(f)

    function_definitions = [
        func
        for func in function_definitions
        if func.get("name") != data.get("function_definition").get("name")
    ]

    function_definitions.append(data.get("function_definition"))

    with open("custom_functions/function_definitions.json", "w") as f:
        json.dump(function_definitions, f, indent=4)

    pythoncode = data.get("python_code")
    with open(
        f"custom_functions/scripts/{data.get('function_definition').get('name')}.py",
        "w",
    ) as f:
        f.write(pythoncode)

    shell_script = data.get("shell_script")

    if shell_script != "":
        result = subprocess.run(
            shell_script, shell=True, capture_output=True, text=True
        )

        if result.returncode == 0:
            return {
                "message": "Script executed successfully",
                "stdout": result.stdout,
            }, 200
        else:
            return {"message": "Script execution failed", "stderr": result.stderr}, 500

    return {"message": "Command executed successfully"}, 200


@app.route("/custom_command", methods=["DELETE"])
def delete_custom_command():
    key = request.get_data(as_text=True)
    function_definitions = []

    with open("custom_functions/function_definitions.json", "r", encoding="utf-8") as f:
        function_definitions = json.load(f)

    function_definitions = [
        function for function in function_definitions if function["name"] != key
    ]

    with open("custom_functions/function_definitions.json", "w") as f:
        json.dump(function_definitions, f, indent=4)

    file_path = f"custom_functions/scripts/{key}.py"
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": "Command deleted successfully"}, 200


@app.route("/get_openai_models", methods=["GET"])
def get_openai_models():
    models = list(get_args(openai.types.chat_model.ChatModel))
    return {"models": models}, 200


def start_flask():
    app.run(
        host="0.0.0.0",
        port=3001,
        ssl_context=("./frontend/cert.pem", "./frontend/key.pem"),
    )
