import webrtcvad
import collections
from pydub import AudioSegment
from transcribe.transcribe import transcribe

vad = webrtcvad.Vad()
vad.set_mode(1)

audio_buffer = collections.deque()
frame_duration_ms = 30  # ms frames for VAD processing
silence_threshold_ms = 500  # Silence streak threshold in ms
noise_floor_buffer = 10  # dB above noise floor to consider valid speech

dynamic_threshold = None

def frame_generator(audio_data, sample_rate):
    """Generates fixed-size audio frames from a continuous stream."""
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
    for i in range(0, len(audio_data), frame_size):
        yield audio_data[i : i + frame_size]


def calculate_dynamic_threshold(audio_segment):
    """Calculate dynamic threshold based on the first second of the audio."""
    noise_floor = audio_segment[:1000].dBFS 
    return noise_floor + 10


def listen(msg, sample_rate):
    global audio_buffer, dynamic_threshold
    audio_buffer.extend(msg)

    audio_segment = AudioSegment(
        data=bytes(audio_buffer), sample_width=2, frame_rate=sample_rate, channels=1
    )

    if len(audio_segment) >= 1000 and dynamic_threshold is None:
        dynamic_threshold = calculate_dynamic_threshold(audio_segment)
        print(f"Initial Dynamic Threshold: {dynamic_threshold:.2f} dBFS")

    if dynamic_threshold is not None and audio_segment.dBFS < dynamic_threshold:
        audio_buffer.clear()
        return None

    normalized_audio = audio_segment
    normalized_audio_bytes = normalized_audio.raw_data
    frames = list(frame_generator(normalized_audio_bytes, sample_rate))

    silence_streak = 0
    voiced_frames = []

    for frame in frames:
        if len(frame) < int(sample_rate * frame_duration_ms / 1000) * 2:
            continue

        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech:
            voiced_frames.append(frame)
            silence_streak = max(0, silence_streak - (frame_duration_ms // 2))
        else:
            silence_streak += frame_duration_ms

        if silence_streak >= silence_threshold_ms and voiced_frames:
            print("Transcribing audio...")
            audio_segment.export("audio_files/recorded_audio.wav", format="wav")
            audio_buffer.clear()
            dynamic_threshold = None
            return transcribe(audio_segment)

    return None
