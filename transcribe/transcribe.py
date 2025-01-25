from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.utils import which
import time
import io
import platform

model_size = "small"
model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

if platform.system() == "Windows":
    AudioSegment.converter = which("transcribe/ffmpeg.exe")
else:
    AudioSegment.converter = which("ffmpeg")


def transcribe(audio_segment):
    start_time = time.time()
    audio_bytes = io.BytesIO()
    audio_segment.export(audio_bytes, format="mp3")
    audio_bytes.seek(0)

    segments, info = model.transcribe(
        audio_bytes,
        beam_size=5,
        vad_filter=False,
        vad_parameters=dict(min_silence_duration_ms=500),
        best_of=5,
        language="en",
    )

    transcribed_segments = [segment.text for segment in segments]

    text = "\n".join(transcribed_segments).strip()

    if not text:
        return None

    print("Transcription: ")
    print(text)

    end_time = time.time()
    transcribe_time = (end_time - start_time) * 1000
    print("Transcription time:", transcribe_time, "ms")

    return text
