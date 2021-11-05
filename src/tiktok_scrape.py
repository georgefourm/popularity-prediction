import datetime
import logging
import os
import time
from csv import DictWriter, DictReader

from src.util import scrape_views


def read_tracks(file: str) -> dict:
    if not os.path.isfile(file):
        logging.info("Data file not found, creating...")
        return dict()

    ids = dict()
    with open(file, mode="r", encoding='utf_8', newline='') as f:
        reader = DictReader(f)
        for line in reader:
            ids[line['id']] = line

    return ids


def download_new_songs(file: str, total_count: int):
    logging.info("Checking existing tracks...")
    all_tracks = read_tracks(file)

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
        write_tracks(file, all_tracks)

    return added


def write_tracks(file, songs_dict):
    with open(file, mode="w", encoding='utf_8', newline='') as f:
        tracks = list(songs_dict.values())
        writer = DictWriter(f, list(tracks[0].keys()))
        writer.writeheader()
        writer.writerows(tracks)


def merge_file(source_file, target_file):
    existing = read_tracks(source_file)
    added, updated = 0, 0
    with open(target_file, 'r', encoding='utf_8', newline='') as file:
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

    write_tracks(target_file, existing)
    logging.info(f"Added {added} new tracks, updated {updated} tracks")


def run(file, chunk, wait, threshold):
    count = threshold + 1
    total = 0
    while count > threshold:
        count = download_new_songs(file, chunk)
        total += count
        logging.info(f"Waiting {wait}s before attempting again")
        time.sleep(wait)
    logging.info(f"Added a total of {total} new tracks")
