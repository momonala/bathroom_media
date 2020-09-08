import json
import logging
from typing import Dict, List

import requests

from values import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PLAYLIST_URI = "59L2W0PlCrvkX7zgq9Bzyv"


class SpotifySearch:
    def __init__(self):
        self.tracks_and_names = self._get_tracks_and_names()

    @staticmethod
    def _get_token() -> Dict:
        url = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        auth = (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        logger.info(f"Making request: {(url, data, auth)}")
        response = requests.post(url, data=data, auth=auth)
        response = json.loads(response.text)
        logger.debug(f"Got response: {response}")
        return response

    @staticmethod
    def _get_tracks(token) -> Dict:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_URI}/tracks"
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"Making request: {(url, headers)}")
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        logger.debug(f"Got response: {response}")
        return response

    def _get_tracks_and_names(self) -> List[Dict]:
        token_resp = self._get_token()
        token = token_resp["access_token"]
        tracks_resp = self._get_tracks(token)
        return [
            {"track": x["track"]["name"], "artist": x["track"]["artists"][0]["name"]}
            for x in tracks_resp["items"]
        ]
