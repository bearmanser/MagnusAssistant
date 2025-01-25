import webrtcvad
import collections
from pydub import AudioSegment
from pydub.playback import play
from transcribe.transcribe import transcribe

vad = webrtcvad.Vad()
vad.set_mode(1)  # 0: Very sensitive, 3: Aggressive filtering

audio_buffer = collections.deque()
frame_duration_ms = 30  # ms frames for VAD processing
silence_threshold_ms = 500  # Reduced silence threshold to consider the end of speech


def frame_generator(audio_data, sample_rate):
    """Generates fixed-size audio frames from a continuous stream."""
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
    for i in range(0, len(audio_data), frame_size):
        yield audio_data[i : i + frame_size]


def listen(msg, sample_rate, volume_threshold=-60):
    global audio_buffer
    audio_buffer.extend(msg.data)

    audio_segment = AudioSegment(
        data=bytes(audio_buffer), sample_width=2, frame_rate=sample_rate, channels=1
    )

    print(f"Volume: {audio_segment.dBFS}")
    if audio_segment.dBFS < volume_threshold:
        audio_buffer.clear()
        return None

    normalized_audio = audio_segment
    normalized_audio_bytes = normalized_audio.raw_data

    frames = list(frame_generator(normalized_audio_bytes, sample_rate))

    silence_streak = 0
    voiced_frames = []

    if audio_segment.duration_seconds < 3:
        return None

    for frame in frames:
        if len(frame) < int(sample_rate * frame_duration_ms / 1000) * 2:
            continue

        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech:
            voiced_frames.append(frame)
            silence_streak = max(
                0, silence_streak - (frame_duration_ms // 2)
            )  # Silence streak with detected speech
        else:
            silence_streak += frame_duration_ms

        if silence_streak >= silence_threshold_ms and voiced_frames:
            audio_buffer.clear()
            print("Transcribing audio...")
            # play(audio_segment)

            return transcribe(audio_segment)

    return None
