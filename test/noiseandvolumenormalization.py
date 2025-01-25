import noisereduce as nr
import numpy as np
from pydub import AudioSegment, effects
from scipy.io import wavfile
from transcribe.transcribe import transcribe


def noise_and_volume_normalization():
    audio_file = "test/output.wav"
    audio_segment = AudioSegment.from_file(audio_file, format="wav")

    # Step 1: Pad the audio with silence (500ms at beginning and end)
    padding_duration = 500  # in milliseconds
    silence = AudioSegment.silent(duration=padding_duration)
    padded_audio_segment = silence + audio_segment + silence

    # Step 2: Apply High-Pass and Low-Pass Filters to Isolate Human Voice Frequencies
    padded_audio_segment = padded_audio_segment.high_pass_filter(300).low_pass_filter(
        3400
    )

    # Step 3: Convert AudioSegment to raw data for further processing
    audio_samples = np.array(padded_audio_segment.get_array_of_samples())
    sample_rate = padded_audio_segment.frame_rate

    # Step 4: Apply Noise Reduction with adjusted parameters for smoother reduction
    reduced_noise_samples = nr.reduce_noise(
        y=audio_samples, sr=sample_rate, prop_decrease=0.9, n_std_thresh_stationary=1.5
    )

    # Step 5: Convert processed numpy array back to AudioSegment
    processed_audio_segment = AudioSegment(
        reduced_noise_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=padded_audio_segment.sample_width,
        channels=padded_audio_segment.channels,
    )

    # Step 6: Apply Volume Normalization
    processed_audio_segment = effects.normalize(processed_audio_segment)

    # Step 7: Apply slight fade in and fade out to smooth out edges
    processed_audio_segment = processed_audio_segment.fade_in(200).fade_out(200)

    # Step 8: Export the processed audio (optional)
    processed_file = "test/processed_audio.wav"
    processed_audio_segment.export(processed_file, format="wav")

    # Step 9: Transcribe the processed audio directly using the AudioSegment object
    print(transcribe(processed_audio_segment))
