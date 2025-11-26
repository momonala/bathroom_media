import glob
import logging
import random
import time
from datetime import datetime

import RPi.GPIO as GPIO
import vlc

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEDIA_DIR = "media/*.mp3"
BUTTON_PIN = 17
RELAY_PIN = 27

instance = vlc.Instance("--aout=alsa", "--alsa-audio-device=hw:0,0")
current_player = instance.media_player_new()  # reuse this for all songs


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)
    time.sleep(0.2)


def turn_on_relay():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    logger.info("🔌 Relay on")


def turn_off_relay():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    logger.info("💤 Relay off")


def wait_for_press():
    while GPIO.input(BUTTON_PIN) == 0:
        time.sleep(0.02)
    while GPIO.input(BUTTON_PIN) == 1:
        time.sleep(0.01)
    logger.info("✅ Button pressed!")


def pick_song():
    audio_files = glob.glob(MEDIA_DIR)
    return random.choice(audio_files) if audio_files else None


def stop_current_playback():
    global current_player
    if current_player.is_playing():
        current_player.stop()


def play_song(path: str):
    global current_player
    hour = datetime.now().hour
    volume = 80 if 9 < hour < 22 else 50

    stop_current_playback()
    media = vlc.Media(path)
    current_player.set_media(media)
    current_player.audio_set_volume(volume)
    current_player.play()
    logger.info(f"🎶 Playing: {path}")
    time.sleep(0.3)  # short delay to ensure the song is playing, since VLC is async


def main():
    setup_gpio()
    logger.info("Ready...")

    try:
        while True:
            wait_for_press()

            song = pick_song()
            if not song:
                logger.error("❌ No audio files found.")
                continue

            turn_on_relay()
            play_song(song)

            # Wait for playback to finish or button press
            while current_player.is_playing():
                if GPIO.input(BUTTON_PIN) == 0:
                    break
                time.sleep(0.05)

            # Playback finished or interrupted
            if not current_player.is_playing():
                logger.info("✅ Playback finished.")
                turn_off_relay()
                time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        stop_current_playback()
        turn_off_relay()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
