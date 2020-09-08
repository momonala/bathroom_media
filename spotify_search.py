import json
import logging
import re
from functools import partial
from string import punctuation
from typing import Dict, List

import requests

from values import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, PLAYLIST_URI

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SpotifySearch:
    def __init__(self):
        self.tracks_and_names = self._get_tracks_and_names()
        logger.info(f"Found tracks: {self.tracks_and_names}")

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
    def _get_tracks(token: str) -> Dict:
        url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_URI}/tracks"
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"Making request: {(url, headers)}")
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        logger.debug(f"Got response: {response}")
        return response

    def _get_tracks_and_names(self) -> List[Dict[str, str]]:
        token_resp = self._get_token()
        token = token_resp["access_token"]
        tracks_resp = self._get_tracks(token)
        parse = partial(re.sub, pattern=fr"[{punctuation}]", repl="")
        return [
            {"track": parse(string=x["track"]["name"]), "artist": parse(string=x["track"]["artists"][0]["name"]),}
            for x in tracks_resp["items"]
        ]
