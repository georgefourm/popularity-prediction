import datetime
import logging
import os
import time

import requests
from progress.bar import Bar

from src.util import read_tracks, write_tracks

API_URL = "https://m.tiktok.com/api/recommend/item_list/"
BATCH_LIMIT = 35  # The TikTok API returns an error on larger batch sizes


def scrape_views(total_count: int) -> list[dict]:
    cookie = os.getenv("TT_COOKIE")
    token = os.getenv('TT_TOKEN', None)
    device_id = os.getenv('TT_DEVICE_ID', None)

    params = {
        "aid": 1988,
        "count": BATCH_LIMIT,
        "verifyFp": token,
        "device_id": device_id
    }

    bar = Bar("Downloading batch...", max=total_count)
    downloaded = []

    while len(downloaded) < total_count:
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


def download_new_tracks(file: str, total_count: int) -> int:
    logging.info("Checking existing tracks...")
    all_tracks = read_tracks(file)
    all_tracks = {track['id']: track for track in all_tracks}

    logging.info("Downloading videos...")
    start = datetime.datetime.now()
    videos = scrape_views(total_count)
    duration = datetime.datetime.now() - start
    logging.info(f"Downloaded {len(videos)} videos in {duration.seconds} seconds")

    added = 0
    updated = 0
    for video in videos:
        track_id = video['music']['id']
        title = video['music']['title']
        album = video['music']['album'] if 'album' in video['music'] else ''
        views = video['stats']['playCount']

        if video['music']['original']:
            continue

        if track_id in all_tracks:
            prev_views = all_tracks[track_id]['views']
            all_tracks[track_id]['views'] = max(int(prev_views), int(views))
            all_tracks[track_id]['videos'] = int(all_tracks[track_id]['videos']) + 1
            updated += 1
            continue

        all_tracks[track_id] = {
            'id': track_id,
            "title": title,
            'album': album,
            'views': int(views),
            'videos': 1
        }
        added += 1

    logging.info(f"Found {added} new tracks, updated {updated} tracks")

    if added > 0 or updated > 0:
        write_tracks(file, list(all_tracks.values()), overwrite=True)

    return added


def run(file, chunk, wait, threshold):
    count = threshold + 1
    total = 0
    while count > threshold:
        count = download_new_tracks(file, chunk)
        total += count
        logging.info(f"Waiting {wait}s before attempting again")
        time.sleep(wait)
    logging.info(f"Added a total of {total} new tracks")
