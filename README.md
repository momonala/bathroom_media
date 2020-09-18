A hacker's way to play music. 

This repo contains logic to generate cached playlists for a raspberry pi to play music on a button click. The idea is that I have a raspberry pi in bathroom with a single button. Click once, play a song, click again, skip to the next song. The music stops when the song is done.

The playlist is generated on Spotify and fetched using their API. Unfortunately, their media player API is for paid accounts only, and I like to pinch pennies. My solution around this is to use their free API to get the playlist information (song title, arist, etc.), then pass that into the YouTube Search API and get the first result. This YouTube URI can be downloaded with YoutubeDL, and cached locally in `/media`. 

Usage: 

1. Install requirements `$pip install -r requirements.txt`
2. Populate `values.py` with your credentials:

```python
SPOTIFY_CLIENT_ID: str = ""
SPOTIFY_CLIENT_SECRET: str = ""
PLAYLIST_URI: str = ""
YOUTUBE_DATA_V3_API_KEY: str = ""
``` 

3. Create cached playlist: `$python download_songs.py`
4. Add a push button to pin 10 on the raspbery pi, and run the player: `$python player.py`