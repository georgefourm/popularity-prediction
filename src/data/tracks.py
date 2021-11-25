import datetime
import logging
import os
import time

import requests
from progress.bar import Bar

from src.data.downloader import DataDownloader
from src.util import read_csv, write_csv

API_URL = "https://m.tiktok.com/api/recommend/item_list/"
BATCH_LIMIT = 35  # The TikTok API returns an error on larger batch sizes
AID = 1988  # Internal application ID, usage is undocumented but requests seem to require it


class TracksDownloader(DataDownloader):

    def __init__(self, output_file: str, threshold: int = 1, wait: int = 10):
        super().__init__(output_file)
        self.threshold = threshold
        self.wait = wait

        tracks = read_csv(self.output_file)
        self.tracks_by_id = {track['id']: track for track in tracks}

    @staticmethod
    def request_items(chunk: int) -> list[dict]:
        cookie = os.getenv("TT_COOKIE")
        token = os.getenv('TT_TOKEN', None)
        device_id = os.getenv('TT_DEVICE_ID', None)

        params = {
            "aid": AID,
            "count": BATCH_LIMIT,
            "verifyFp": token,
            "device_id": device_id
        }

        bar = Bar("Downloading batch...", max=chunk)
        downloaded = []

        while len(downloaded) < chunk:
            requests.head(API_URL, params=params)

            headers = {
                "cookie": cookie
            }

            response = requests.get(API_URL, params=params, headers=headers)

            content = response.json()
            items = content['itemList']

            if len(items) == 0:
                break

            bar.next(len(items))
            downloaded += items

        bar.finish()

        return downloaded

    def update_tracks(self, chunk: int) -> tuple[int, int]:
        logging.info("Downloading videos...")
        start = datetime.datetime.now()
        videos = self.request_items(chunk)
        duration = datetime.datetime.now() - start
        logging.info(f"Downloaded {len(videos)} videos in {duration.seconds} seconds")

        added = 0
        updated = 0
        tracks = self.tracks_by_id

        for video in videos:
            music = video['music']
            track_id = music['id']

            if track_id is None or music['original']:
                continue

            title = music['title']
            album = music['album'] if 'album' in music else ''
            views = video['stats']['playCount']

            if track_id in tracks:
                prev_views = tracks[track_id]['views']
                tracks[track_id]['views'] = max(int(prev_views), int(views))
                tracks[track_id]['videos'] = int(tracks[track_id]['videos']) + 1
                updated += 1
                continue

            tracks[track_id] = {
                'id': track_id,
                "title": title,
                'album': album,
                'views': int(views),
                'videos': 1
            }
            added += 1

        logging.info(f"Found {added} new data points, updated {updated}")

        return added, updated

    def run(self, chunk: int = 100, limit: int = None):
        added = self.threshold + 1
        total_added = 0
        total_updated = 0

        while added > self.threshold:
            added, updated = self.update_tracks(chunk)

            total_added += added
            total_updated += updated

            if added > 0 or updated > 0:
                tracks = list(self.tracks_by_id.values())
                write_csv(self.output_file, tracks, overwrite=True)

            if limit is not None and total_added >= limit:
                break

            logging.info(f"Waiting {self.wait}s before attempting again")
            time.sleep(self.wait)

        logging.info(f"Added a total of {total_added} new data points, updated {total_updated} total data points.")
