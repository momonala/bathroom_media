import logging
import os
from typing import Dict

import youtube_dl
from youtubesearchpython import VideosSearch

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def download_youtube_video_if_needed(search_terms: Dict):
    search_terms_str = f"{search_terms['track']} {search_terms['artist']}"
    logger.info(f"Searching Youtube for {search_terms_str=}")
    video_params = _youtube_search(search_terms_str)
    _download_youtube_video(video_params, search_terms_str)


def _youtube_search(search_terms: str) -> Dict[str, str]:
    # return {"id": "0XlUsEfcKB0", "title": "test video"}
    video_search_results = VideosSearch(search_terms, limit=1)
    single_response = video_search_results.result()["result"][0]
    return {"id": single_response["id"], "title": single_response["title"]}


def _download_youtube_video(video_params: Dict[str, str], search_terms_str: str) -> None:
    mp3_output = f"media/{video_params['id']}_{search_terms_str.replace(' ', '')}.mp3"
    if os.path.exists(mp3_output):
        logger.info(f"File {mp3_output} already exists. Skipping.")
        return

    options = {
        # todo youtube-dl issue, cant download only audio, getting codec
        # issue
        "outtmpl": "%(id)s" + ".mp4",
        "format": "bestaudio/best",
    }
    youtube_url = f'https://www.youtube.com/watch?v={video_params["id"]}'
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([youtube_url])
        logger.info(f"Sucessfully downloaded video file {video_params}.")
    try:
        # use ffmpeg to conver the .mp4 file to a .mp3
        os.system(f'ffmpeg -y -i {video_params["id"]}.mp4 -f mp3 -ab 192000 -vn {mp3_output}')
    except FileNotFoundError as e:
        logger.error(f"Conversion failed for {video_params['id']}.")
        raise e

    # clean up
    os.remove(video_params["id"] + ".mp4")
    logger.info(f"Sucessfully saved audio for {mp3_output}!")
