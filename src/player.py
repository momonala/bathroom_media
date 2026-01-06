"""
Bathroom Music Button - GPIO-triggered music player for Raspberry Pi.

Use Case:
1. Wait for button press (GPIO 17, pulled up - press pulls LOW)
2. On press: activate relay (GPIO 27), play random song
3. While playing, if button pressed again: skip to next song, keep relay on
4. When song finishes naturally (no skip): deactivate relay
5. Relay stays on as long as user keeps skipping through songs

Hardware:
- Button: GPIO 17 (internal pull-up, active LOW)
- Relay: GPIO 27 (HIGH = on during playback)
- Speaker: Pi audio output via ALSA
"""

import glob
import logging
import random
import time
from datetime import datetime
from typing import Optional

import RPi.GPIO as GPIO
import vlc

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEDIA_DIR = "media/*.mp3"
BUTTON_PIN = 17
RELAY_PIN = 27

# Volume settings
VOLUME_DAY = 80
VOLUME_NIGHT = 50
DAY_START_HOUR = 9
DAY_END_HOUR = 22

# Audio device
ALSA_DEVICE = "hw:0,0"

instance = vlc.Instance("--aout=alsa", f"--alsa-audio-device={ALSA_DEVICE}")
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


def is_button_pressed() -> bool:
    """Button is active LOW (pressed = 0, released = 1 due to pull-up)."""
    return GPIO.input(BUTTON_PIN) == 0


def wait_for_button_press() -> None:
    """
    Block until user presses and releases the button.

    Momentary button with pull-up resistor:
    - Released: reads HIGH (1)
    - Pressed: reads LOW (0)

    We wait for both press AND release to:
    1. Avoid multiple triggers from one press
    2. Handle mechanical bounce
    """
    # Wait for press (HIGH → LOW)
    while not is_button_pressed():
        time.sleep(0.02)

    # Wait for release (LOW → HIGH)
    while is_button_pressed():
        time.sleep(0.01)

    logger.info("✅ Button pressed!")


def pick_song() -> Optional[str]:
    audio_files = glob.glob(MEDIA_DIR)
    return random.choice(audio_files) if audio_files else None


def stop_current_playback():
    global current_player
    if current_player.is_playing():
        current_player.stop()


def play_song(path: str):
    global current_player
    hour = datetime.now().hour
    volume = VOLUME_DAY if DAY_START_HOUR < hour < DAY_END_HOUR else VOLUME_NIGHT

    stop_current_playback()
    media = vlc.Media(path)
    current_player.set_media(media)
    current_player.audio_set_volume(volume)
    current_player.play()
    logger.info(f"🎶 Playing: {path}")
    time.sleep(0.3)  # short delay to ensure the song is playing, since VLC is async


def wait_for_playback_or_skip() -> bool:
    """
    Block while song is playing. Return True if user skipped, False if song ended naturally.

    Also handles button debounce on skip (waits for release).
    """
    while current_player.is_playing():
        if is_button_pressed():
            # Wait for release to debounce
            while is_button_pressed():
                time.sleep(0.01)
            return True  # skipped
        time.sleep(0.05)
    return False  # finished naturally


def play_until_done() -> None:
    """
    Play songs in a loop until one finishes without being skipped.

    - On skip: pick new song, keep playing
    - On natural end: return (caller should turn off relay)
    """
    song = pick_song()
    if not song:
        logger.error("❌ No audio files found.")
        return

    while True:
        play_song(song)

        if wait_for_playback_or_skip():
            logger.info("⏭️ Skipping to next song...")
            song = pick_song()
            if not song:
                logger.error("❌ No audio files found.")
                return
        else:
            logger.info("✅ Playback finished.")
            return


def main() -> None:
    setup_gpio()
    logger.info("Ready...")

    try:
        while True:
            wait_for_button_press()
            turn_on_relay()
            play_until_done()
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
