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

1. Install requirements (python 3) `pip install -r requirements.txt`
2. Populate `values.py` with your credentials:
```python
SPOTIFY_CLIENT_ID: str = ""
SPOTIFY_CLIENT_SECRET: str = ""
PLAYLIST_URI: str = ""
``` 

3. Run `mkdir media`
4. Create cached media playlist: `python download_songs.py`
5. Install `mpv` command line music player: `sudo apt-get install mpv`
6. Install MQTT pub/sub service (and debugging tools): `sudo apt-get install mosquitto mosquitto-clients -y`
7. Update MQTT config `/etc/mosquitto/conf.d/mosquitto.conf` to listen to external ports with:

```
listener 1883
allow_anonymous true
```
7. Setup `systemd` to run MQTT and `player.py` as background services:
   1. create the file: `/lib/systemd/system/mqtt.service`. Note that we manually set our config file with `-c`.
```
 [Unit]
 Description=Custom MQTT Server
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=sudo mosquitto -c /etc/mosquitto/conf.d/mosquitto.conf
 User=pi

 [Install]
 WantedBy=multi-user.target
```
   3. create the file `/lib/systemd/system/bathroom_button.service`
```
[Unit]
 Description=Bathroom Button
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/usr/bin/python3 /home/pi/bathroom_media/player.py > /home/pi/logs/bathroom_player.log 2>&1
 User=pi

 [Install]
 WantedBy=multi-user.target
```
8. Start the services. In the terminal execute:
```
sudo chmod 644 /lib/systemd/system/mqtt.service
sudo chmod 644 /lib/systemd/system/bathroom_button.service

sudo systemctl daemon-reload

sudo systemctl enable mqtt.service
sudo systemctl enable bathroom_button.service

sudo reboot
```
The services are now running in the background! You should be able to click your button and live happily again.
