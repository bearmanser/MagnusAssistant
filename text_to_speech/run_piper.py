import datetime
import json
import subprocess
import time
import os
import asyncio


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
