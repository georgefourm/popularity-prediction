import datetime
import logging
import os
import time
from csv import DictWriter, DictReader
from dotenv import load_dotenv

from TikTokApi import TikTokApi

DATA_FILE = "data/raw/tracks.csv"


def read_tracks() -> dict:
    if not os.path.isfile(DATA_FILE):
        print("Data file not found, creating...")
        return dict()

    ids = dict()
    with open(DATA_FILE, mode="r", encoding='utf_8', newline='') as f:
        reader = DictReader(f)
        for line in reader:
            ids[line['id']] = line

    return ids


def download_new_songs(total_count: int, region: str):
    token = os.getenv('TT_TOKEN', None)
    device_id = os.getenv('TT_DEVICE_ID', None)
    cookie = os.getenv('TT_COOKIE')

    api = TikTokApi.get_instance(
        custom_verifyFp=token,
        custom_device_id=device_id,
        logging_level=logging.INFO,
    )

    print("Checking existing tracks...")
    all_tracks = read_tracks()

    print("Downloading videos...")
    start = datetime.datetime.now()
    videos = api.by_trending(
        count=total_count,
        region=region,
        cookie=cookie
    )
    duration = datetime.datetime.now() - start
    print(f"Downloaded {len(videos)} videos in {duration.seconds} seconds")

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

    print(f"Found {added} new tracks, updated {updated} tracks")

    if added > 0 or updated > 0:
        write_tracks(all_tracks)

    return added


def write_tracks(songs_dict):
    with open(DATA_FILE, mode="w", encoding='utf_8', newline='') as file:
        tracks = list(songs_dict.values())
        writer = DictWriter(file, list(tracks[0].keys()))
        writer.writeheader()
        writer.writerows(tracks)


def merge_file(source_file):
    existing = read_tracks()
    added, updated = 0, 0
    with open(source_file, 'r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            track_id = line['id']
            if line['id'] in existing:
                prev_views = existing[track_id]['views']
                existing[track_id]['views'] = max(int(prev_views), int(line['views']))
                existing[track_id]['videos'] = int(existing[track_id]['videos']) + 1
                updated += 1
            else:
                existing[line['id']] = {
                    'id': line['id'],
                    "title": line['title'],
                    'album': line['album'],
                    'views': int(line['views']),
                    'videos': 1
                }
                added += 1

    write_tracks(existing)
    print(f"Added {added} new tracks, updated {updated} tracks")


if __name__ == "__main__":
    load_dotenv()
    chunk = 1000
    threshold = 1
    wait = 10
    count = threshold + 1
    total = 0
    while count > threshold:
        print(f"Waiting {wait}s before attempting again")
        time.sleep(wait)
        count = download_new_songs(chunk, region='GB')
        total += count
    print(f"Added a total of {total} new tracks")
    exit(0)
