import random
import threading
import aiohttp
from aiohttp import web
import numpy as np
from faster_whisper import WhisperModel
from openwakeword import Model
import resampy
import argparse
import json
import webrtcvad
from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_silence
from openai_api import ask_openai
from endpoints.Endpoints import start_flask
from home_assistant.run_ha import run_ha
from intent_recognition.intent_recognition import intent_recognition
from text_to_speech.run_piper import run_piper

audio_buffer = []
vad = webrtcvad.Vad(3)
listening = False

model_size = "tiny.en"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--chunk_size",
    help="How much audio (in number of samples) to predict on at once",
    type=int,
    default=1280,
    required=False
)
parser.add_argument(
    "--model_path",
    help="The path of a specific model to load",
    type=str,
    default="",
    required=False
)
parser.add_argument(
    "--inference_framework",
    help="The inference framework to use (either 'onnx' or 'tflite'",
    type=str,
    default='tflite',
    required=False
)
args = parser.parse_args()
owwModel = Model(wakeword_models=["config/wake_word_files/meeji.onnx"])


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_str(json.dumps({"loaded_models": list(owwModel.models.keys())}))

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            sample_rate = int(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f"WebSocket error: {ws.exception()}")
        else:
            prediction = await predict(msg, sample_rate)
            if prediction is not None:
                await ws.send_str(prediction)
                wav_file = listen(msg, sample_rate)
                if wav_file is not None:
                    await ws.send_str("Audio ready")
    return ws


async def predict(msg, sample_rate):
    audio_bytes = msg.data

    if len(msg.data) % 2 == 1:
        audio_bytes += b'\x00'

    data = np.frombuffer(audio_bytes, dtype=np.int16)
    if sample_rate != 16000:
        data = resampy.resample(data, sample_rate, 16000)

    predictions = owwModel.predict(data)

    for key in predictions:
        if predictions[key] >= 0.5:
            return json.dumps({"activations": key})


def listen(msg, sample_rate):
    global audio_buffer
    global listening
    if not listening:
        print("Listening")
        listening = True
    audio_buffer.extend(msg.data)
    audio_segment = AudioSegment(bytes(audio_buffer), sample_width=2, frame_rate=sample_rate, channels=1)

    chunks = split_on_silence(audio_segment, min_silence_len=500, silence_thresh=-40, keep_silence=True)
    speech_periods = False
    for chunk in chunks:
        if chunk.dBFS > -40:
            speech_periods = True

    silence_ranges = detect_silence(audio_segment, min_silence_len=500, silence_thresh=-40)

    if speech_periods and silence_ranges and silence_ranges[-1][1] == len(audio_segment):
        listening = False
        audio_buffer = []
        return transcribe(audio_segment)


def transcribe(audio_segment):
    print("Transcribing")
    audio_mp3 = audio_segment.export("output.mp3", format="mp3")

    segments, info = model.transcribe(audio_mp3, beam_size=20, vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500), best_of=10)
    transcribed_segments = []

    for segment in segments:
        transcribed_segments.append(segment.text)

    text = '\n'.join(transcribed_segments)
    if text == "" or text == " ":
        return

    print("Transcription:")
    print(text)

    try:
        command = intent_recognition(text)
        run_ha(command)
        responses = [
            "Sure",
            "Of course",
            "Absolutely",
            "Certainly",
            "No problem",
            "Yes, definitely",
            "Yes master",
            "Alright",
            "Okay",
            "Certainly, I can do that",
            "Sure thing",
            "Yep, I can do that",
            "Affirmative",
            "You got it",
            "Roger that",
            "Roger, roger",
            "Consider it done",
            "Very well",
            "As you wish",
            "Absolutely, without a doubt",
            "Indeed",
            "Without question",
        ]

        response = random.choice(responses)
    except:
        response = ask_openai(text)

    print(response)

    return run_piper(response)


async def static_file_handler(request):
    return web.FileResponse('test/templates/index.html')


def run_test():
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler), web.get('/', static_file_handler)])

    web.run_app(app, host='localhost', port=9000)
