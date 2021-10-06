import datetime
import os
import time

import progress
from csv import DictWriter, DictReader

from TikTokApi import TikTokApi

FILE = "data/raw/songs.csv"


def get_existing_songs() -> dict:
    if not os.path.isfile(FILE):
        return dict()

    ids = dict()
    with open(FILE, mode="r", encoding='utf_8', newline='') as f:
        reader = DictReader(f)
        for line in reader:
            ids[line['id']] = line

    return ids


def download_new_songs(total_count, region):
    api = TikTokApi.get_instance(custom_verifyFp="verify_kufa5jz5_7u4Ag1Tc_H51O_4oqO_8zpW_5TMeuQULc12q")

    print("Checking existing songs...")
    unique_songs = get_existing_songs()

    print("Downloading videos...")
    start = datetime.datetime.now()
    videos = api.by_trending(count=total_count, region=region)
    duration = datetime.datetime.now() - start
    print(f"Downloaded {len(videos)} videos in {duration.seconds} seconds")

    added = 0
    updated = 0
    for video in videos:
        song_id = video['music']['id']
        title = video['music']['title']
        album = video['music']['album'] if 'album' in video['music'] else ''
        views = video['stats']['playCount']

        if video['music']['original']:
            continue

        if song_id in unique_songs:
            prev_views = unique_songs[song_id]['views']
            unique_songs[song_id]['views'] = max(int(prev_views), int(views))
            unique_songs[song_id]['videos'] = int(unique_songs[song_id]['videos']) + 1
            updated += 1
            continue

        unique_songs[song_id] = {
            'id': song_id,
            "title": title,
            'album': album,
            'views': int(views),
            'videos': 1
        }
        added += 1

    print(f"Found {added} new tracks, updated {updated} tracks")

    if added > 0 or updated > 0:
        write_songs(unique_songs)

    return added


def write_songs(songs_dict):
    with open(FILE, mode="w", encoding='utf_8', newline='') as file:
        tracks = list(songs_dict.values())
        writer = DictWriter(file, list(tracks[0].keys()))
        writer.writeheader()
        writer.writerows(tracks)


def merge_file(source_file):
    existing = get_existing_songs()
    added, updated = 0, 0
    with open(source_file, 'r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            song_id = line['id']
            if line['id'] in existing:
                prev_views = existing[song_id]['views']
                existing[song_id]['views'] = max(int(prev_views), int(line['views']))
                existing[song_id]['videos'] = int(existing[song_id]['videos']) + 1
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

    write_songs(existing)
    print(f"Added {added} new songs, updated {updated} songs")


if __name__ == "__main__":
    chunk = 1000
    threshold = 20
    wait = 10
    count = threshold + 1
    while count > threshold:
        count = download_new_songs(chunk, region='GB')
        print(f"Waiting {wait}s before attempting again")
        time.sleep(wait)
