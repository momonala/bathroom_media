A hacker's way to listen to music in the toilet. 

Sometimes you want music in the bathroom, but you dont want to deal with chosing a song, connecting your phone (or a friend's) to bluetooth, pausing when you're done, etc. This repo has the solution. This is an overenginered approach to do one thing: play a song when a button is pressed!

Our button is connected to a low-power ESP8266 microcontroller, which sends a message to a headless Raspberry Pi server connected to a speaker. This server has a Spotify-synced playlist and a MQTT pub/sub service for receiving messages from the ESP8266. When a message is recieved, it is played via the UNIX command line music player, `mpv`. Additional button-clicks will skip to the next song.

The playlist is generated on Spotify and can be periodically synced locally. Unfortunately, Spotify's media player API is for paid accounts only, and I like to pinch pennies. My solution around this is to use their free API to get the playlist information (song title, arist, etc.), then pass that into YouTube Search and get the first result. This YouTube URI can be downloaded with YoutubeDL, and cached locally in `/media`.
 
# Setup:

## Setup ESP8266:
1. Hookup push button to Pin 15
2. add in relevant SSID/password into  `esp_mqtt_buttom/arduino_secrets.h`
3. upload Arduino sketch

## Setup Raspberry Pi: 

1. Install requirements (python 3) `poetry install`
2. Populate `values.py` with your credentials:
```python
SPOTIFY_CLIENT_ID: str = ""
SPOTIFY_CLIENT_SECRET: str = ""
PLAYLIST_URI: str = ""
```

3. Populate `arduino_secrets.h` with your credentials:
```c++
#define SECRET_SSID "SSID"
#define SECRET_PASS "PASSOWRD"
``` 

4. Run `mkdir media`
5. Create cached media playlist: `python download_songs.py`
6. Install `ffmpeg, madplay, mqtt`: `sudo apt-get install ffmpeg madplay mosquitto mosquitto-clients -y`
7. Update MQTT config to listen to external ports with: `sudo nano /etc/mosquitto/conf.d/mosquitto.conf`

```
listener 1883
allow_anonymous true
```

8. Setup `systemd` to run MQTT and `player.py` as background services:
    1. create the file: `/lib/systemd/system/mqtt.service`. Note that we manually set our config file with `-c`.
```
 [Unit]
 Description=Custom MQTT Server
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=sudo mosquitto -c /etc/mosquitto/conf.d/mosquitto.conf
 User=tinybathroom

 [Install]
 WantedBy=multi-user.target
```

   2. create the file `/lib/systemd/system/projects_bathroom_button.service`
```
[Unit]
 Description=Bathroom Button
 After=multi-user.target

 [Service]
 WorkingDirectory=/home/tinybathroom/bathroom_button
 Type=idle
 ExecStart=/home/mnalavadi/.local/bin/uv run python player.py
 User=tinybathroom

 [Install]
 WantedBy=multi-user.target
```
9. Start the services. In the terminal execute:
```
sudo chmod 644 /lib/systemd/system/mqtt.service
sudo chmod 644 /lib/systemd/system/projects_bathroom_button.service

sudo systemctl daemon-reload
sudo systemctl daemon-reexec

sudo systemctl enable mqtt.service
sudo systemctl enable projects_bathroom_button.service

sudo reboot
```

10. View logs:
```
journalctl -u mqtt.service
journalctl -u projects_bathroom_button.service

The services are now running in the background! You should be able to click your button and live happily again.
