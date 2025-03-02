import datetime
import os
from collections import deque
import numpy as np
import resampy
from openwakeword import Model
import time

from config.config import get_config_value

wake_word_dir = "config/wake_word_files/"
wake_word_files = [
    os.path.join(root, file_name)
    for root, _, files in os.walk(wake_word_dir)
    for file_name in files
]

owwModel = Model(
    wakeword_models=wake_word_files,
    inference_framework="onnx",
)

recent_volumes = deque(maxlen=10)
prev_volume_above_threshold = False


recent_data = deque(maxlen=3)


async def predict(msg, sample_rate, min_volume_threshold=20):
    global prev_volume_above_threshold
    global recent_volumes
    global recent_data

    audio_bytes = msg.data

    if len(msg.data) % 2 == 1:
        audio_bytes += b"\x00"

    data = np.frombuffer(audio_bytes, dtype=np.int16)

    if data.size == 0 or np.isnan(data).any() or np.isinf(data).any():
        return None

    rms_volume = np.sqrt(np.mean(data.astype(np.float64) ** 2))
    recent_volumes.append(rms_volume)

    if (
        rms_volume < min_volume_threshold
        and not prev_volume_above_threshold
        or len(recent_volumes) < 10
    ):
        prev_volume_above_threshold = False
        return None

    prev_volume_above_threshold = rms_volume >= min_volume_threshold

    if sample_rate != 16000:
        data = resampy.resample(data, sample_rate, 16000)

    recent_data.append(data)
    combined_data = np.concatenate(list(recent_data))

    predictions = owwModel.predict(combined_data)

    for key in predictions:
        if predictions[key] >= get_assistant_from_wake_word(key).get(
            "wake_word_sensitivity", 0.5
        ):
            return key


last_update_time = 0
assistants_cache = {}
wake_word_folder_map = {}


def get_cache():
    global last_update_time, assistants_cache, wake_word_folder_map
    if time.time() - last_update_time >= 10:
        assistants_cache = get_config_value("assistants")
        wake_word_folder_map = {
            file.replace(".onnx", ""): os.path.basename(root)
            for root, _, files in os.walk("config/wake_word_files")
            for file in files
            if file.endswith(".onnx")
        }
        last_update_time = time.time()
    return assistants_cache, wake_word_folder_map


def get_assistant_from_wake_word(wake_word):
    assistants_cache, wake_word_folder_map = get_cache()

    folder_id = wake_word_folder_map.get(wake_word)
    if not folder_id:
        return None

    for _, assistant_data in assistants_cache.items():
        if assistant_data.get("wake_word") == folder_id:
            return assistant_data

    return None
