import subprocess
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartHandler(FileSystemEventHandler):
    def __init__(self, process_callback):
        super().__init__()
        self.process_callback = process_callback

    def on_modified(self, event):
        ignored_files = [
            "key.pem",
            "cert.pem",
            "ffmpeg.exe",
            "package.json",
            "config.json",
            "voices.json",
        ]
        ignored_dirs = [
            "venv",
            ".git",
            "__pycache__",
            ".vscode",
            ".idea",
            "frontend",
            "ha_data",
            "node_modules",
            "custom_functions",
            "piper_windows",
            "piper_linux",
            "piper_files",
            "wake_word_files",
        ]

        if (
            not event.is_directory
            and not any(
                ignored_file in event.src_path for ignored_file in ignored_files
            )
            and not any(
                ignored_dir in os.path.normpath(event.src_path).split(os.sep)
                for ignored_dir in ignored_dirs
            )
        ):
            print(f"File {event.src_path} changed, restarting main script..")
            self.process_callback()


def start_script():
    venv_python = "venv/Scripts/python.exe"
    return subprocess.Popen([venv_python, "main.py"])


def main():
    process = start_script()

    def restart_process():
        nonlocal process
        if process:
            process.terminate()
            process.wait()
        process = start_script()

    event_handler = RestartHandler(restart_process)
    path_to_watch = os.path.abspath(".")
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if process:
            process.terminate()
    observer.join()


if __name__ == "__main__":
    main()
