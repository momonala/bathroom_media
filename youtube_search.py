import json
import logging
import os
from typing import Dict
from glob import glob
import re
import googleapiclient.discovery
import youtube_dl

from values import YOUTUBE_DATA_V3_API_KEY

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YouTubeSearch:
    def __init__(self, search_terms: dict):
        self.search_terms = search_terms
        self.search_terms_str = f"{search_terms['track']} {search_terms['artist']}"
        self.video = None
        self.cached_songs = [
            re.search(r"_(.*).mp3", x).groups()[0] for x in glob("media/*mp3")
        ]
        if "".join(self.search_terms_str.split()) in self.cached_songs:
            logger.info(f"Found cached {self.search_terms_str}")
        else:
            self.search_and_download()

    def search_and_download(self):
        self.video = self._search()
        self._download_youtube_video()

    def to_dict(self) -> Dict:
        return self.video

    def to_json(self) -> str:
        return json.dumps({"videos": self.video})

    def _search(self) -> Dict[str, str]:
        return {"id": "0XlUsEfcKB0", "title": "test video"}
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=YOUTUBE_DATA_V3_API_KEY, cache_discovery=False
        )

        request = youtube.search().list(
            part="snippet", q=self.search_terms, type="video", maxResults=1,
        )
        response = request.execute()
        video_id = response["items"][0]["id"]["videoId"]
        title = response["items"][0]["snippet"]["title"]
        logger.info(f"Youtube V3 API results: {video_id, title}")
        return {"id": video_id, "title": title}

    def _download_youtube_video(self) -> None:
        mp3_output = (
            f"media/{self.video['id']}_{self.search_terms_str.replace(' ', '')}.mp3"
        )
        if os.path.exists(mp3_output):
            logger.info(f"File {mp3_output} already exists. Skipping.")
            return

        options = {
            # todo youtube-dl issue, cant download only audio, getting codec issue
            "outtmpl": "%(id)s" + ".mp4",
            "format": "bestaudio/best",
        }
        youtube_url = f'https://www.youtube.com/watch?v={self.video["id"]}'
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([youtube_url])
            logger.info(f"Sucessfully downloaded video file {self.video}.")
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
