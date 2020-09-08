import json
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
        youtube_search_results = pool.map(YouTubeSearch, s.tracks_and_names)
    song_metadata = [x.to_dict() for x in youtube_search_results]

    with open("song_metadata.json", "w") as filehandle:
        filehandle.write(json.dumps(song_metadata, indent=4))
    logging.info("Saved metadata file to song_metadata.json")


if __name__ == "__main__":
    _download_all_songs()
