import glob
import subprocess

import logging
import time
from itertools import cycle
from random import shuffle

import paho.mqtt.client as mqtt

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MQTT_SERVER = "192.168.0.183"
MQTT_TOPIC = "home/bathroom_button"
MQTT_PORT = 1883


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server."""
    client.subscribe(MQTT_TOPIC)
    logger.info(f'Connected to MQTT: {MQTT_SERVER=} {MQTT_TOPIC=} {MQTT_PORT=} {rc=}')


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    logger.info(f"Received message: {msg.topic=} {msg.payload=}")
    _file = next(userdata['audio_files'])
    subprocess.Popen(f"pkill mpv".split())  # kill the old player process
    time.sleep(.1)
    subprocess.Popen(f"mpv {_file}".split())  # start a new one
    logger.info(f"playing: {_file}")


if __name__ == "__main__":
    # cycle through .mp3 files in /media, skip song if event trigger
    audio_files = glob.glob("media/*mp3")
    shuffle(audio_files)
    audio_files = cycle(audio_files)

    # setup MQTT client and subscribe to messages
    mqtt_client = mqtt.Client(userdata={"audio_files": audio_files})
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_SERVER, 1883)
    mqtt_client.loop_forever()
