import logging
import os
from typing import Iterator

import spotipy
from progress.bar import Bar
from spotipy import SpotifyClientCredentials

from src.data.downloader import DataDownloader
from src.util import read_csv

SPOTIFY_MAX_TRACKS = 100


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

            search_results = self.api.search(q=track['title'], type='track')

            if search_results['tracks']['total'] == 0:
                continue

            item = search_results['tracks']['items'][0]
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
