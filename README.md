# Bathroom Music Button

A simple hacker's way to have music in your bathroom.

Sometimes you want music in the bathroom but don’t want to deal with choosing a song, connecting your phone, or manually pausing playback. This project plays a random song **whenever you press a physical button** — using a Raspberry Pi, a push button, a relay, and a speaker.

---

## How it works

- A **physical push button** is connected to a Raspberry Pi GPIO pin.  
- When pressed, the Pi plays a random song from a locally cached playlist using **VLC**.  
- A **relay** turns on whenever a song is playing and turns off when playback stops.  
- Songs are stored in `/media` as local MP3 files.

---

## Hardware

- Raspberry Pi (headless or with desktop)  
- Push button  
- Relay module to drive an external device (optional, for LED or sound indicator)  
- Speaker connected to Pi’s audio output

**GPIO pin connections:**

| Component | GPIO Pin |
|-----------|----------|
| Button    | 17       |
| Relay     | 27       |

---

## Workflow Diagram

```mermaid
flowchart TD
    A[Button Pressed (GPIO 17)] --> B[Pi detects press]
    B --> C[Pick random MP3 from /media]
    C --> D[Stop current playback if any]
    D --> E[Set new media to VLC MediaPlayer]
    E --> F[Start playback]
    F --> G[Turn on relay (GPIO 27)]
    F --> H[Monitor playback]
    H -->|Finished| I[Turn off relay]
    H -->|Button pressed again| D


## Setup

### 1. Install dependencies
./install/install.sh

### 2. Prepare media folder
python download_songs.py

### 3. Connect hardware

- Wire the button to GPIO 17 (with a pull-up resistor).

- Wire the relay to GPIO 27.

- The relay will automatically turn on when a song is playing and off when it finishes.

### 4. Configure and run the script

`python player.py`

Press the button to play songs. The relay will indicate playback.

5. Run as a background service

#### Create a systemd service: `/lib/systemd/system/bathroom_button.service`

```
[Unit]
Description=Bathroom Music Button
After=multi-user.target

[Service]
WorkingDirectory=/home/tinybathroom/bathroom_media
Type=idle
ExecStart=/home/tinybathroom/.cache/pypoetry/virtualenvs/bathroom-media-*/bin/python player.py
User=tinybathroom

[Install]
WantedBy=multi-user.target
```

#### Enable and start the service:

```
sudo chmod 644 /lib/systemd/system/bathroom_button.service
sudo systemctl daemon-reload
sudo systemctl enable bathroom_button.service
sudo systemctl start bathroom_button.service
```

#### View logs:

`journalctl -u bathroom_button.service -f`


Now the script runs in the background — pressing the button will play a song and toggle the relay automatically.

## Notes

- Songs are chosen randomly from /media/*.mp3.

- Volume is adjusted based on the time of day (daytime vs night).

- VLC is used directly with ALSA (--aout=alsa) to ensure audio works headless on a Raspberry Pi.
