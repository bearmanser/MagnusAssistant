import json
import os
import subprocess
import time
import wave

def append_audio_to_existing(existing_file, new_audio_data, sample_rate=22050):
    """Append new audio data to an existing WAV file."""
    with wave.open(existing_file, "rb") as wav_file:
        params = wav_file.getparams()
        existing_audio = wav_file.readframes(wav_file.getnframes())

    with wave.open(existing_file, "wb") as wav_file:
        wav_file.setparams(params)
        wav_file.writeframes(existing_audio + new_audio_data)

def get_total_duration(folder):
    total_duration = 0
    for filename in os.listdir(folder):
        base, ext = os.path.splitext(filename)
        if ext.lower() == ".wav" and base != "greeting" and base != "recorded_audio":
            file_path = os.path.join(folder, filename)
            try:
                with wave.open(file_path, "rb") as wav_file:
                    duration = wav_file.getnframes() / wav_file.getframerate()
                    total_duration += duration
            except wave.Error:
                continue
    return total_duration

async def run_piper_save_to_file(
    assistant,
    text: str = "I didn't get any text to speak.",
    output_folder: str = "audio_files",
    duration_threshold: int = 20,
    file_name: str | None = None
):
    start_time = time.time()
    sanitized_text = text.replace("\n", " ").replace("\r", "")

    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    if not file_name: 
        highest_number = 0
        for filename in os.listdir(output_folder):
            base, ext = os.path.splitext(filename)
            if ext.lower() == ".wav":
                try:
                    num = int(base)
                    if num > highest_number:
                        highest_number = num
                except ValueError:
                    continue

        new_number = highest_number + 1
        output_file_path = os.path.join(output_folder, f"{new_number}.wav")
    else:
        output_file_path = os.path.join(output_folder, file_name)

    total_duration = get_total_duration(output_folder)

    if os.name == "nt":
        model = os.path.join(
            "..", "..", "config", "piper_files", assistant["voice"], f"{assistant['voice']}.onnx"
        )
        command = f'echo "{sanitized_text}" | piper.exe -m "{model}" --output_raw'
        cwd = "text_to_speech/piper_windows"

        process = subprocess.Popen(
            command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        raw_output, error_output = process.communicate()

        if process.returncode == 0:
            sample_rate = 22050
            if total_duration >= duration_threshold:
                existing_file_path = os.path.join(output_folder, f"{highest_number}.wav")
                append_audio_to_existing(existing_file_path, raw_output, sample_rate)
                print(f"Appended to existing file: {existing_file_path}")
            else:
                with wave.open(output_file_path, "wb") as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit audio
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(raw_output)
                print(f"Created new file: {output_file_path}")
        else:
            print(f"Error: {error_output.decode()}")
    else:  # Linux
        model = os.path.join(
            "..",
            "..",
            "..",
            "config",
            "piper_files",
            assistant["voice"],
            f"{assistant['voice']}.onnx",
        )
        # Using the absolute path for the output file ensures that piper saves it correctly.
        command = f'echo "{sanitized_text}" | ./piper -m "{model}" --output_file "{output_file_path}"'
        cwd = os.path.join("text_to_speech", "piper_linux", "piper")
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.wait()

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    return output_file_path


if __name__ == "__main__":
    run_piper_save_to_file({
                "name": "Miji",
                "personality": "You are Miji, a virtual assistant who is not only clear and precise but also warm, friendly, and approachable. Miji responds as if speaking to a friend, using natural, conversational language and everyday phrasing.\n\nVoice and Personality Guidelines:\n\nEach response should be:\n- Warm, empathetic, and patient.\n- Proactive in clarifying complex ideas with phrases like, \"I understand that might be confusing—let me break it down for you.\"\n- Informal and relaxed, using contractions and a natural tone that makes the conversation feel human and engaging.\n\nFormatting and Conversion Guidelines:\n\n- Write everything as it would be spoken aloud.\n- Convert numbers, fractions, times, dates, symbols, and abbreviations into full phrases for clarity.\n  - For example, “1 3/4 cups” should be read as “one and three-quarters cups.”\n- For times, use informal phrasing such as “three twenty in the afternoon” rather than military or formal time.\n- For dates, use full written-out formats, e.g., “October twenty-seventh, twenty twenty-four,” instead of numeric formats.\n- Clarify ambiguous terms by providing context.\n  - For instance, read “km” as “kilometers” and “3.14” as “three point one four” in mathematical contexts.\n- Simplify long numbers and decimals to approximate values when possible, using scientific notation only if clarity requires it.\n- Avoid ranges, symbols, and abbreviations that could disrupt the natural spoken flow.\n\nOverall Interaction Guidelines:\n\n- Each response should be short, precise, and flow naturally in conversation, with each sentence beginning on a new line.\n- Prioritize clarity and simplicity while retaining a friendly tone.\n- Confirm or recheck information when prompted to ensure accuracy in simple terms.",
                "language": "English",
                "wake_word": "miji",
                "voice": "en_US-hfc_female-medium"
            }, "Hello, world!", "C:/Users/omgri/Documents/GitHub/MagnusAssistant/audio_files")

async def run_piper(ws, assistant, text: str = "I didn't get any text to speak."):
    print(text)
    start_time = time.time()
    sanitized_text = text.replace("\n", " ").replace("\r", "")

    if os.name == "nt":  # Windows

        model = (
            "../../config/piper_files/"
            + assistant["voice"]
            + "/"
            + assistant["voice"]
            + ".onnx"
        )
        command = f"echo {sanitized_text} | piper.exe -m {model} --output_raw"
        cwd = "text_to_speech/piper_windows"
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            for chunk in iter(lambda: process.stdout.read(8192), b""):
                await ws.send_bytes(chunk)
            await ws.send_str(json.dumps({"__END_OF_STREAM__": True}))
        except Exception as e:
            print(e)
        finally:
            process.stdout.close()
            process.wait()

    else:  # Linux
        model = (
            "../../../config/piper_files/"
            + assistant["voice"]
            + "/"
            + assistant["voice"]
            + ".onnx"
        )
        output_file = "audio.wav"
        command = (
            f'echo "{sanitized_text}" | ./piper -m {model} --output_file {output_file}'
        )

        cwd = "text_to_speech/piper_linux/piper"
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        process.wait()  # Wait for piper to finish generating the file

        if os.path.exists(os.path.join(cwd, output_file)):
            try:
                with open(os.path.join(cwd, output_file), "rb") as audio_file:
                    while chunk := audio_file.read(256):
                        await ws.send_bytes(chunk)
            except Exception as e:
                print(e)

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
