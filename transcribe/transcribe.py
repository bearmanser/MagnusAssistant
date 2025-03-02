from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.utils import which
import time
import io
import platform

model = WhisperModel("medium")

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


def transcribe_wav_file(file_path):
    """
    Transcribes a .wav file using faster_whisper and pydub.

    :param file_path: Path to the .wav file to transcribe.
    :return: Transcribed text or None if no text is found.
    """
    start_time = time.time()

    try:
        # Load .wav file as an AudioSegment
        audio_segment = AudioSegment.from_wav(file_path)

        # Convert the AudioSegment to bytes (mp3 format for faster_whisper)
        audio_bytes = io.BytesIO()
        audio_segment.export(audio_bytes, format="mp3")
        audio_bytes.seek(0)

        # Transcribe the audio
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

        # print("Transcription: ")
        # print(text)

        end_time = time.time()
        transcribe_time = (end_time - start_time) * 1000
        # print("Transcription time:", transcribe_time, "ms")

        return text

    except Exception as e:
        print(f"Error while transcribing {file_path}: {e}")
        return None


if __name__ == "__main__":
    file_path = (
        "C:/Users/omgri/Documents/GitHub/MagnusAssistant/audio_files/recorded_audio.wav"
    )

    models = [
        # "tiny.en",
        # "tiny",
        # "base.en",
        # "base",
        "small.en",
        "small",
        "medium.en",
        "medium",
        "large-v1",
        "large-v2",
        "large-v3",
        "large",
        "distil-large-v2",
        "distil-medium.en",
        "distil-small.en",
        "distil-large-v3",
    ]

    for model_name in models:
        model = WhisperModel(model_name, device="cuda", compute_type="int8_float16")

        start_time = time.time()
        transcription = transcribe_wav_file(file_path)
        end_time = time.time()
        print(
            "Model: " + model_name + ", Transcription: " + transcription + ", Time:",
            end_time - start_time,
            "s",
        )
