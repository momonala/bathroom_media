import logging
from multiprocessing import Pool

from spotify_search import SpotifySearch
from youtube_search import YouTubeSearch

POOL_SIZE = 5

logging.basicConfig()
logger = logging.getLogger(__name__)


def _download_all_songs() -> None:
    s = SpotifySearch()

    with Pool(POOL_SIZE) as pool:
        pool.map(YouTubeSearch, s.tracks_and_names)


if __name__ == "__main__":
    _download_all_songs()
