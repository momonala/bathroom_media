import logging
import os
from glob import glob
from multiprocessing import Pool, cpu_count

from spotify_search import SpotifySearch
from youtube_search import download_youtube_video_if_needed, parse_search_terms

POOL_SIZE = cpu_count()

logging.basicConfig()
logger = logging.getLogger(__name__)


def _download_all_songs() -> None:
    s = SpotifySearch()
    to_be_cached = [parse_search_terms(x)[1] for x in s.tracks_and_names]
    existing_cache = glob("media/*mp3")
    to_delete = set(existing_cache) - set(to_be_cached)
    [os.remove(f) for f in to_delete]

    with Pool(POOL_SIZE) as pool:
        pool.map(download_youtube_video_if_needed, s.tracks_and_names)


if __name__ == "__main__":
    _download_all_songs()
