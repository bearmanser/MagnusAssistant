import datetime
import os
from collections import deque
import numpy as np
import resampy
from openwakeword import Model
import time

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

    rms_volume = np.sqrt(np.mean(data**2))
    recent_volumes.append(rms_volume)
    avg_recent_volume = np.mean(recent_volumes)

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

    # Add the current data to recent_data and combine the last 3 messages
    recent_data.append(data)
    combined_data = np.concatenate(list(recent_data))

    predictions = owwModel.predict(combined_data)

    for key in predictions:
        if predictions[key] >= 0.7:
            return key
