import logging
import os
from typing import Iterator

import spotipy, re
from progress.bar import Bar
from spotipy import SpotifyClientCredentials

from src.data.downloader import DataDownloader
from src.util import read_csv

SPOTIFY_MAX_TRACKS = 100
PARENS_REGEX = re.compile(r"\(.*\)")


def find_best_match(track: dict, search_results: list[dict]):
    best_match = search_results[0]
    best_score = 0.0

    title = track['title'].lower().strip()
    title_bare = PARENS_REGEX.sub("", title).strip()
    album = str(track['album']).lower().strip() if track['album'] is None else None

    heuristics = [
        (lambda i: title == i['title'], 1),
        (lambda i: (title + " ") in i['title'], .5),
        (lambda i: title_bare == i['title'], .3),
        (lambda i: (title_bare + " ") in i['title'], .3),
        (lambda i: album is not None and album == i['album'], 1),
        (lambda i: album is not None and (album + " ") in i['album'], .5)
    ]

    for result in search_results:
        candidate = {
            'title': result['name'].lower().strip(),
            'album': result['album']['name'].lower().strip()
        }
        score = sum([heuristic[1] for heuristic in heuristics if heuristic[0](candidate)])
        if score > best_score:
            best_score = score
            best_match = result

    return best_match


class FeatureDownloader(DataDownloader):
    def __init__(self, output_file: str, tracks_file: str):
        super().__init__(output_file)

        tracks = read_csv(tracks_file, strict=True)
        features = read_csv(self.output_file, strict=False)

        existing_ids = {feature['tt_id'] for feature in features}
        new_tracks = [track for track in tracks if track['id'] not in existing_ids]

        logging.info(f"{len(new_tracks)} new tracks found since last run")
        self.new_tracks = new_tracks

        credentials = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        self.api = spotipy.Spotify(auth_manager=credentials)

    def download(self) -> Iterator[dict]:
        batch = []

        tracks = self.new_tracks

        bar = Bar('Downloading track features...', max=len(tracks))
        for i, track in enumerate(tracks):
            bar.next()

            search_results = self.api.search(q=track['title'], type='track', limit=50)

            if search_results['tracks']['total'] == 0:
                continue

            item = find_best_match(track, search_results['tracks']['items'])

            if item is None:
                continue

            batch.append({
                'id': item['id'],
                'tt_id': track['id'],  # Keep ID for cross-reference
                'title': item['name'],
                'album': item['album']['name'],
                'artist': ", ".join([artist['name'] for artist in item['artists']]),
                'popularity': item['popularity']
            })

            # Download audio features per batch or when reaching the last track, for efficiency
            if len(batch) % SPOTIFY_MAX_TRACKS == 0 or i == len(tracks) - 1:
                ids = [item['id'] for item in batch]
                feature_results = self.api.audio_features(ids)
                for idx, features in enumerate(feature_results):
                    if features is None:
                        continue

                    item = batch[idx]
                    yield {**item, **features}

                batch = []
