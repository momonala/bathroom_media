import logging
from multiprocessing import Pool, cpu_count

from spotify_search import SpotifySearch
from youtube_search import download_youtube_video_if_needed

POOL_SIZE = cpu_count()

logging.basicConfig()
logger = logging.getLogger(__name__)


def _download_all_songs() -> None:
    s = SpotifySearch()

    with Pool(POOL_SIZE) as pool:
        pool.map(download_youtube_video_if_needed, s.tracks_and_names)


if __name__ == "__main__":
    _download_all_songs()
