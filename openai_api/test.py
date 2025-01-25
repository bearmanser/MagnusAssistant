import re
import threading
from queue import Queue

import openai_api
from pydub.playback import play

from text_to_speech.run_piper import run_piper

openai_api.api_key = "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"

response = ""
last_desired_segment = ""
audio_queue = Queue()


def audio_player():
    while True:
        if not audio_queue.empty():
            audio_clip = audio_queue.get()
            play(audio_clip)


def process_response(response_text):
    global last_desired_segment
    segments = response_text.split("\n")
    if len(segments) >= 2:
        second_last_segment = segments[-2]
        if second_last_segment != last_desired_segment and second_last_segment != '':
            audio_clip = run_piper(second_last_segment.strip())
            audio_queue.put(audio_clip)
            last_desired_segment = second_last_segment

