import glob
import logging
import random
import subprocess
import time
from datetime import datetime

import paho.mqtt.client as mqtt

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MQTT_SERVER = "192.168.2.107"
MQTT_TOPIC = "home/bathroom_button"
MQTT_PORT = 1883


def on_connect(client, _, __, rc):
    """The callback for when the client receives a CONNACK response from the server."""
    client.subscribe(MQTT_TOPIC)
    logger.info(f'Connected to MQTT: {MQTT_SERVER=} {MQTT_TOPIC=} {MQTT_PORT=} {rc=}')


def on_message(_, __, msg):
    """The callback for when a PUBLISH message is received from the server.
    Cycle through .mp3 files in /media, skip song if event trigger.
    """
    logger.info(f"Received message: {msg.topic=} {msg.payload=}")
    audio_files = glob.glob("media/*mp3")
    _file = random.choice(audio_files)
    subprocess.Popen(f"pkill madplay".split())  # kill the old player process
    time.sleep(.1)
    volume = -1 if 9 < datetime.now().hour < 22 else -10  # half the volume if its very late/early
    subprocess.Popen(f"madplay {_file} -a {volume}".split())  # start a new song
    logger.info(f"playing: {_file}")


if __name__ == "__main__":
    # setup MQTT client and subscribe to messages
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_SERVER, 1883)
    mqtt_client.loop_forever()
