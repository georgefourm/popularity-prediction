import json
import logging
import os
import time
from typing import Iterator

import requests
from progress.bar import Bar

from src.data.downloader import DataDownloader
from src.util import read_csv


class TagDownloader(DataDownloader):

    def __init__(self, output_file: str, features_file: str, wait: int = 5):
        super().__init__(output_file)
        self.wait_secs = wait

        tracks = read_csv(features_file, strict=True)
        tags = read_csv(self.output_file, strict=False)

        existing_ids = {tag['id'] for tag in tags}
        new_tracks = [track for track in tracks if track['id'] not in existing_ids]

        logging.info(f"{len(new_tracks)} new tracks found since last run")
        self.new_tracks = new_tracks

    def download(self) -> Iterator[dict]:
        url = os.getenv("LASTFM_API_URL")
        api_key = os.getenv("LASTFM_API_KEY")
        common_params = {
            'api_key': api_key,
            'format': 'json',
        }

        tracks = self.new_tracks

        bar = Bar(message="Downloading tags", max=len(tracks))
        for track in tracks:
            time.sleep(self.wait_secs)

            response = requests.get(url, params={
                **common_params,
                'method': 'track.search',
                'track': track['title'],
                'artist': track['artist']
            })
            info = response.json()
            track_matches = info['results']['trackmatches']

            if 'track' not in track_matches or len(track_matches['track']) == 0:
                continue

            track_info = track_matches['track'][0]

            tag_info = requests.get(url, params={
                **common_params,
                'method': 'track.gettoptags',
                'track': track_info['name'],
                'artist': track_info['artist']
            }).json()

            if 'toptags' not in tag_info or len(tag_info['toptags']['tag']) == 0:
                continue

            tags = tag_info['toptags']['tag']
            bar.next()

            yield {
                'id': track['id'],
                'title': track_info['name'],
                'artist': track_info['artist'],
                'listeners': track_info['listeners'],
                'tags': json.dumps(tags)
            }
