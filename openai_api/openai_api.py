import asyncio
from datetime import datetime, timedelta
import importlib
import json
import re
from queue import Queue
import time
import openai
from pydub.playback import play
from config.config import get_config_value
from custom_functions.custom_functions import (
    get_custom_functions,
)
from text_to_speech.run_piper import run_piper
import json
from num2words import num2words


last_desired_segment = ""
audio_queue = Queue()
conversation_history = []
openai.api_key = get_config_value("openai.api_key")

TOKEN_LIMIT = 128000


def estimate_token_count(text: str) -> int:
    return len(text) // 4


def audio_player():
    while True:
        if not audio_queue.empty():
            audio_clip = audio_queue.get()
            play(audio_clip)


async def process_response(response_text, ws, assistant):
    global last_desired_segment

    non_speech_symbols_pattern = r"(?<!\b\w)[.?!:;](?!\s|$|,)"
    year_formatting_pattern = r"(\b\d{2})(\d{2}\b)"
    number_pattern = r"\b\d+\b"
    formatted_response = re.sub(non_speech_symbols_pattern, "", response_text)
    formatted_response = re.sub(year_formatting_pattern, r"\1 \2", formatted_response)

    def replace_number_with_words(match):
        number = int(match.group(0))
        return num2words(number)

    formatted_response = re.sub(
        number_pattern, replace_number_with_words, formatted_response
    )
    formatted_response = re.sub(r"\n\s*\n", "\n", formatted_response)

    segments = formatted_response.split("\n")
    if len(segments) >= 2:
        second_last_segment = segments[-2]
        if second_last_segment != last_desired_segment and second_last_segment != "":
            last_desired_segment = second_last_segment
            await ws.send_str(json.dumps({"response": second_last_segment.strip()}))
            await asyncio.create_task(
                run_piper(ws, assistant, second_last_segment.strip())
            )


def add_message(role, content, name=None):
    return {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "name": name,
    }


def trim_conversation_history(messages, token_limit, assistant, lifetime=2):
    time_threshold = datetime.now() - timedelta(minutes=lifetime)

    messages = [
        m
        for m in messages
        if "timestamp" in m
        and isinstance(m["timestamp"], str)
        and datetime.fromisoformat(m["timestamp"]) >= time_threshold
    ]

    newest_user_index = max(
        (i for i, m in enumerate(messages) if m["role"] == "user"), default=None
    )

    prefix = assistant["personality"] + " Now answer this prompt: "
    for i, message in enumerate(messages):
        if (
            i != newest_user_index
            and message["role"] == "user"
            and prefix in message["content"]
        ):
            message["content"] = message["content"].replace(prefix, "", 1)

    total_token_count = sum(estimate_token_count(m["content"]) for m in messages)

    while total_token_count > token_limit and len(messages) > 1:
        removed_message = messages.pop(1)
        total_token_count -= estimate_token_count(removed_message["content"])

    return messages


async def ask_openai(
    message: str, ws, assistant, role: str = "user", function_name: str = None
):
    global conversation_history

    if function_name:
        conversation_history.append(add_message("function", message, function_name))
    else:
        conversation_history.append(
            add_message(
                role, assistant["personality"] + " Now answer this prompt: " + message
            )
        )

    if len(conversation_history) > 6:
        conversation_history = conversation_history[-6:]

    messages = []
    messages.extend(conversation_history)

    messages = trim_conversation_history(messages, TOKEN_LIMIT, assistant)

    try:
        response_stream = openai.chat.completions.create(
            model=get_config_value("openai.model"),
            messages=messages,
            functions=get_custom_functions(),
            function_call="auto",
            stream=True,
        )

        current_message = ""
        function_call_name = None
        function_call_arguments_str = ""

        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                current_message += chunk.choices[0].delta.content
                await process_response(current_message, ws, assistant)

            if chunk.choices[0].delta.function_call:
                if chunk.choices[0].delta.function_call.name:
                    function_call_name = chunk.choices[0].delta.function_call.name
                if chunk.choices[0].delta.function_call.arguments:
                    function_call_arguments_str += chunk.choices[
                        0
                    ].delta.function_call.arguments

        if current_message:
            await process_response(current_message + "\n", ws, assistant)
            conversation_history.append(add_message("assistant", current_message))

            if current_message.rstrip().endswith("?"):
                from websocket.websocket_handler import set_listening

                time.sleep(5)
                await set_listening(True, ws)
                await ws.send_str(json.dumps({"activation": True}))
                print("setting listening to True")

        if function_call_name and function_call_arguments_str:
            try:
                function_arguments = json.loads(function_call_arguments_str)
                print(
                    f"Function call triggered: {function_call_name} with arguments {function_arguments}"
                )
                process_function_call(
                    function_call_name, function_arguments, ws, assistant
                )
            except json.JSONDecodeError as e:
                print(f"JSON decode error after accumulation: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        return
    except Exception as e:
        print(e)


def process_function_call(function_name, function_arguments, ws, assistant):
    module = importlib.import_module(f"custom_functions.scripts.{function_name}")
    function_to_call = getattr(module, function_name)
    try:
        if function_arguments and callable(function_to_call):
            import inspect

            sig = inspect.signature(function_to_call)
            if len(sig.parameters) > 0:
                result = function_to_call(**function_arguments)
            else:
                result = function_to_call()
        else:
            result = function_to_call()
    except Exception as e:
        result = {"error": str(e), "type": type(e).__name__}

    asyncio.create_task(
        ask_openai(
            json.dumps(result),
            ws,
            assistant,
            role="function",
            function_name=function_name,
        )
    )
