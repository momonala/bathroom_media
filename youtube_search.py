import json
import logging
import os
import urllib.parse
from typing import List, Dict

import requests
import youtube_dl
from bs4 import BeautifulSoup

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YouTubeSearch:
    def __init__(self, search_terms: dict, download: bool = True):
        self.download = download
        self.search_terms = search_terms
        self.search_terms_str = f"{search_terms['track']} {search_terms['artist']}"
        self.video = self._search()
        if self.download and self.video:
            self._download_youtube_video()

    def to_dict(self) -> Dict:
        return self.video

    def to_json(self) -> str:
        return json.dumps({"videos": self.video})

    def _search(self) -> Dict:
        encoded_search = urllib.parse.quote(self.search_terms_str)
        url = f"https://youtube.com/results?search_query={encoded_search}&pbj=1"
        logger.info(f"Making request: {url}")
        response = requests.get(url).text
        logger.debug(f"Got response: {response}")
        response = BeautifulSoup(response, "html.parser")
        results = self._parse_html(response)
        if not results:
            return {}
        return {**results[0], **self.search_terms}

    @staticmethod
    def _parse_html(soup) -> List:
        results = []
        for video in soup.select(".yt-uix-tile-link"):
            if video["href"].startswith("/watch?v="):
                video_info = {
                    "title": video["title"],
                    "link": video["href"],
                    "id": video["href"][video["href"].index("=") + 1 :],
                }
                results.append(video_info)
        return results

    def _download_youtube_video(self) -> None:
        mp3_output = f"media/{self.video['id']}.mp3"
        if os.path.exists(mp3_output):
            logger.info(f"File {mp3_output} already exists. Skipping.")
            return

        options = {
            # todo youtube-dl issue, cant download only audio, getting codec issue
            "outtmpl": "%(id)s" + ".mp4",
            "format": "bestaudio/best",
        }
        youtube_url = f'https://www.youtube.com/{self.video["link"]}'
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([youtube_url])
            logger.info(f'Sucessfully downloaded video file {self.video["link"]}.')
        try:
            # use ffmpeg to conver the .mp4 file to a .mp3
            os.system(
                f'ffmpeg -y -i {self.video["id"]}.mp4 -f mp3 -ab 192000 -vn {mp3_output}'
            )
        except FileNotFoundError as e:
            logger.error(f"Conversion failed for {self.video['id']}.")
            raise e

        # clean up
        os.remove(self.video["id"] + ".mp4")
        logger.info(f"Sucessfully saved audio for {mp3_output}!")
