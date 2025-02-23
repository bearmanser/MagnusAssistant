import asyncio
import json
import base64
import time
import audioop
import os
from aiohttp import web
from twilio.rest import Client

from config.config import get_config_value
from listen.listen import listen
from openai_api.openai_api import ask_openai

PUBLIC_BASE_URL = get_config_value("twilio.base_url")
TWILIO_ACCOUNT_SID = get_config_value("twilio.account_sid")
TWILIO_AUTH_TOKEN = get_config_value("twilio.auth_token")
CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

RECORDING_FILE = "recorded_audio.wav"
AUDIO_FOLDER = "audio_files"


stream_available = asyncio.Event()
stream_available.set()
active_stream = {"ws": None, "call_sid": None}


def get_lowest_audio_file():
    try:
        files = os.listdir(AUDIO_FOLDER)
    except Exception:
        return None
    lowest_number = None
    lowest_file = None
    for file in files:
        if file.endswith(".wav"):
            try:
                num = int(os.path.splitext(file)[0])
            except ValueError:
                continue
            if lowest_number is None or num < lowest_number:
                lowest_number = num
                lowest_file = file
    return lowest_file


async def ws_handler(request):
    global active_stream
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    delete_all_audio_files()
    print("New WebSocket connection established.")
    active_stream["ws"] = ws
    start_time = time.time()
    local_call_sid = None
    transcription = None
    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=1)
            except asyncio.TimeoutError:
                msg = None
            except Exception as e:
                if ws.closed:
                    break
                else:
                    print("WebSocket connection error:", e)
                    break
            if msg is not None:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if not local_call_sid and data.get("event") == "start":
                            local_call_sid = data.get("start", {}).get("callSid")
                            if local_call_sid:
                                active_stream["call_sid"] = local_call_sid
                            print("Call SID from start event:", local_call_sid)
                        if data.get("event") == "media":
                            payload = data.get("media", {}).get("payload")
                            if payload:
                                raw_audio = base64.b64decode(payload)
                                pcm_chunk = audioop.ulaw2lin(raw_audio, 2)
                                transcription = listen(pcm_chunk, 8000)
                                if transcription:
                                    break
                    except Exception as e:
                        print("Error processing message:", e)
                elif msg.type == web.WSMsgType.ERROR:
                    print("WebSocket connection closed with exception:", ws.exception())
                    break
            if time.time() - start_time >= 20:
                break
    except Exception as e:
        if not ws.closed:
            print("WebSocket connection error:", e)
    finally:
        try:
            if transcription:
                assistant = get_config_value("twilio.assistant")
                asyncio.create_task(
                    ask_openai(transcription, None, assistant, send_to_websocket=False)
                )
        except Exception as file_err:
            print("Error processing transcription:", file_err)
        await ws.close()
        stream_available.set()
        if active_stream["ws"] == ws:
            active_stream["ws"] = None
    if local_call_sid:
        twiml_response = f"""<Response>
                                    <Redirect>{PUBLIC_BASE_URL}/next-twiml</Redirect>
                                </Response>"""
        try:
            CLIENT.calls(local_call_sid).update(twiml=twiml_response)
            print(f"Updated call {local_call_sid} with redirect to /next-twiml.")
        except Exception as e:
            print("Error updating call:", e)
    else:
        if active_stream["call_sid"]:
            try:
                CLIENT.calls(active_stream["call_sid"]).update(
                    twiml=f"""<Response>
                                    <Redirect>{PUBLIC_BASE_URL}/next-twiml</Redirect>
                                </Response>"""
                )
                print(
                    f"Updated call {active_stream['call_sid']} with redirect to /next-twiml."
                )
            except Exception as e:
                print("Error updating call with global call_sid:", e)
        else:
            print("No call SID available; cannot update call with new TwiML.")
    return ws


def delete_all_audio_files():
    try:
        for file in os.listdir(AUDIO_FOLDER):
            if file.endswith(".wav") and file != "greeting.wav" and file != "recorded_audio.wav":
                os.remove(os.path.join(AUDIO_FOLDER, file))
        print("All audio files deleted.")
    except Exception as e:
        print(f"Error deleting audio files: {e}")


async def serve_audio(request):
    file_param = request.match_info.get("file")
    filename = os.path.join(AUDIO_FOLDER, file_param)
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                file_data = f.read()
            os.remove(filename)
            print(f"Served and deleted file: {filename}")
            return web.Response(body=file_data, content_type="audio/wav")
        except Exception as e:
            print(f"Error serving file {filename}: {e}")
            return web.Response(status=500, text="Error serving file.")
    else:
        return web.Response(status=404, text="File not found.")


async def greeting(request):
    filename = os.path.join(AUDIO_FOLDER, "greeting.wav")
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                file_data = f.read()
            return web.Response(body=file_data, content_type="audio/wav")
        except Exception as e:
            print(f"Error serving file {filename}: {e}")
            return web.Response(status=500, text="Error serving file.")
    else:
        return web.Response(status=404, text="File not found.")


async def next_twiml(request):
    global active_stream
    data = await request.post()
    if "CallSid" in data:
        active_stream["call_sid"] = data["CallSid"]

    try:
        files = os.listdir(AUDIO_FOLDER)
        audio_files = sorted(
            [file for file in files if file.endswith(".wav") and file != "greeting.wav" and file != "recorded_audio.wav"], 
            key=lambda x: int(os.path.splitext(x)[0])
        )
    except Exception as e:
        print(f"Error listing audio files: {e}")
        audio_files = []

    if audio_files:
        play_tags = "\n".join(
            [f"<Play>{PUBLIC_BASE_URL}/audio/{file}</Play>" for file in audio_files]
        )
        twiml_response = f"""<Response>
                                {play_tags}
                                <Redirect>{PUBLIC_BASE_URL}/next-twiml</Redirect>
                            </Response>"""
        print(f"Returning TwiML to play files: {', '.join(audio_files)}")
    else:
        if active_stream["ws"] is not None and not active_stream["ws"].closed:
            print("Stream already active; ending it to start a new one.")
            await active_stream["ws"].close()
            active_stream["ws"] = None
            stream_available.set()
            await asyncio.sleep(0.5)
        stream_available.clear()
        wss_url = PUBLIC_BASE_URL.replace("https://", "wss://") + "/stream"
        twiml_response = f"""<Response>
                                <Start>
                                    <Stream url="{wss_url}">
                                        <Parameter name="callSid" value="{active_stream["call_sid"]}" />
                                    </Stream>
                                </Start>
                                <Pause length="3600"/>
                            </Response>"""
        print("Starting a new stream.")

    return web.Response(text=twiml_response, content_type="application/xml")


app = web.Application()
app.router.add_get("/stream", ws_handler)
app.router.add_get("/audio/{file}", serve_audio)
app.router.add_get("/greeting", greeting)
app.router.add_post("/next-twiml", next_twiml)


def start_twilio():
    if PUBLIC_BASE_URL and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        web.run_app(app, port=6000)


if __name__ == "__main__":
    start_twilio()
