import asyncio
import json
import random

from home_assistant.get_ha_helper import post_ha_conversation
from home_assistant.run_ha import run_ha
from intent_recognition.intent_recognition import intent_recognition
from openai_api.openai_api import ask_openai
from text_to_speech.run_piper import run_piper


async def handle_transcription_result(text, ws, assistant):
    # This commented code was used for Home Assistant intent recognition, 
    # tho it's not used anymore in favor of OpenAI function calling.

    # try:
    #     ha_conversation_result = post_ha_conversation(text)
    #     if ha_conversation_result and ha_conversation_result.get("response", {}).get(
    #         "data", {}
    #     ).get("success"):
    #         response = ha_conversation_result["response"]["speech"]["plain"]["speech"]
    #     else:
    #         command = intent_recognition(text)
    #         run_ha(command)
    #         responses = [
    #             "Sure",
    #             "Yes master",
    #             "Alright",
    #             "Okay",
    #             "Roger, roger",
    #             "As you wish",
    #         ]
    #         response = random.choice(responses)

    #     print(response)
    #     await ws.send_str(json.dumps({"response": response}))
    #     await asyncio.create_task(run_piper(ws, assistant, response))

    # except Exception as e_outer:
    #     print(f"An error occurred: {e_outer}")
    await ask_openai(text, ws, assistant=assistant)
