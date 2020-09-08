import glob
import os
import subprocess
import time
from itertools import cycle
from random import shuffle
from typing import Callable


def _get_event_handler() -> Callable:
    """Return an event handler based on OS (Mac vs Linux)"""
    return {"Darwin": input, "Linux": _wait_for_button}.get(os.uname()[0])


def _wait_for_button():
    import RPi.GPIO as GPIO
    import time

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        if GPIO.input(10) == GPIO.HIGH:
            print("Button was pushed!")
            time.sleep(0.2)
            return True


if __name__ == "__main__":
    # cycle through .mp3 files in /media, skip song if event trigger
    audio_files = glob.glob("media/*mp3")
    shuffle(audio_files)
    audio_files = cycle(audio_files)
    event_handler = _get_event_handler()

    while True:
        _file = next(audio_files)
        print(f"playing {_file}")
        p = subprocess.Popen(f"mpv {_file}".split())
        event_handler()
        p.terminate()
        time.sleep(1)
