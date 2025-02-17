import asyncio
import json
import os
import ssl
import time

import aiohttp
from aiohttp import web
import openai

from config.config import get_config_value
from listen.listen import listen
from openai_api.openai_api import ask_openai
from wake_word.predict import predict, recent_volumes, recent_data

sample_rate = 48000
listening = False
listening_start_time = None


async def set_listening(value, ws):
    global listening
    listening = value


async def websocket_handler(request):
    try:
        global sample_rate
        global listening
        global listening_start_time
        message_count = 0
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        assistant = None
        async for msg in ws:
            message_count += 1

            if msg.type == aiohttp.WSMsgType.TEXT:
                sample_rate = int(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
            elif not listening:
                if (
                    listening_start_time is None
                    or (time.time() - listening_start_time) >= 3
                    and message_count > 10
                ):
                    prediction = await predict(msg, sample_rate)
                    if prediction is not None:
                        await ws.send_str(json.dumps({"activation": prediction}))
                        print("listening set to True")
                        listening = True
                        listening_start_time = time.time()
                        message_count = 0
                        recent_volumes.clear()
                        recent_data.clear()

                        asyncio.ensure_future(stop_listening_after_delay(15, ws))

                        folder_id = [
                            os.path.basename(root)
                            for root, _, files in os.walk("config/wake_word_files")
                            if f"{prediction}.onnx" in files
                        ]
                        folder_id = folder_id[0] if folder_id else None

                        for assistant_value in get_config_value("assistants").values():
                            if assistant_value["wake_word"] == folder_id:
                                assistant = assistant_value
                                break

            if listening:
                print("listening")
                transcription = listen(msg.data, sample_rate)
                if transcription is not None and transcription != "":

                    listening = False
                    print("Sending transcription")
                    await ws.send_str(json.dumps({"transcription": transcription}))
                    await ask_openai(transcription, ws, assistant=assistant)

    except asyncio.TimeoutError:
        raise TimeoutError("WebSocket connection timed out")
    except Exception as e:
        print(e)


async def stop_listening_after_delay(delay, ws):
    try:
        global listening
        global listening_start_time
        await asyncio.sleep(delay)
        if listening and (time.time() - listening_start_time >= delay):
            print("Stopping listening")
            listening = False
            await ws.send_str(json.dumps({"stop_listening": True}))
    except Exception as e:
        print(e)


async def generate_code_websocket_handler(request):
    try:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                message = json.loads(msg.data)
                if "prompt" in message:
                    prompt = message["prompt"]
                    response_stream = openai.chat.completions.create(
                        model=get_config_value("openai.model"),
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                    )
                for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        await ws.send_str(
                            json.dumps({"code": chunk.choices[0].delta.content})
                        )
                if chunk.choices[0].finish_reason == "stop":
                    await ws.close()

    except Exception as e:
        print(e)


app = web.Application()
app.add_routes(
    [
        web.get("/ws", websocket_handler),
        web.get("/generate_code", generate_code_websocket_handler),
    ]
)


def start_websocket_server():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain("frontend/cert.pem", "frontend/key.pem")

    web.run_app(app, host="0.0.0.0", port=5000, ssl_context=ssl_context)


if __name__ == "__main__":
    start_websocket_server()
