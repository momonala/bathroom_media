import glob
import logging
import random
import subprocess
import time
from datetime import datetime

import RPi.GPIO as GPIO

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEDIA_DIR = "media/*.mp3"
BUTTON_PIN = 17
RELAY_PIN = 27
MAX_VOLUME = 32768  # mpg123 max volume


def pick_song():
    audio_files = glob.glob(MEDIA_DIR)
    return random.choice(audio_files) if audio_files else None


def play_song_and_wait_till_done(path: str) -> None:
    # stop any old playback
    subprocess.Popen(["pkill", "mpg123"])
    time.sleep(0.1)

    hour = datetime.now().hour
    volume = 1 if 9 < hour < 22 else 0.5
    logger.info(f"🎶 Playing: {path}")

    proc = subprocess.Popen([
        "mpg123",
        "-f",
        str(int(volume * MAX_VOLUME)),
        "-a",
        "plughw:Device,0",
        path
    ])
    proc.wait()
    logger.info(f"✅ Playback of {path} finished.")


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)
    time.sleep(0.2)  # allow pin to settle at startup


def turn_on_relay():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    logger.info("🔌 Relay turned on!")


def turn_off_relay():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    logger.info("💤 Relay turned off!")


def wait_for_press():
    # make sure button is not already pressed at start
    while GPIO.input(BUTTON_PIN) == 0:
        time.sleep(0.05)

    # now wait for actual press
    GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING, bouncetime=300)
    logger.info("✅ Button pressed!")


def main():
    setup_gpio()
    logger.info("Ready. Waiting for button...")

    try:
        while True:
            wait_for_press()

            song = pick_song()
            if not song:
                logger.error("❌ No audio files found.")
                continue

            turn_on_relay()
            play_song_and_wait_till_done(song)
            turn_off_relay()
            time.sleep(0.2)  # debounce buffer

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
