import logging
import os
from csv import DictReader

import spotipy
from progress.bar import Bar
from spotipy.oauth2 import SpotifyClientCredentials

from src.util import read_tracks, write_tracks


def update_existing_tracks(output_file: str, tracks: list[dict]) -> list[dict]:
    existing = []
    tracks_by_id = {track['id']: track for track in tracks}

    if not os.path.isfile(output_file):
        return existing

    with open(output_file, mode='r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            if line['tt_id'] in tracks_by_id:
                track = tracks_by_id[line['tt_id']]
                line['views'] = track['views']
                line['videos'] = track['videos']
            else:
                logging.warning(f"Track ID {line['tt_id']} ({line['title']}) not found in scraped view data"
                                f", but exists in full data. This might happen if view data was deleted/modified")
            existing.append(line)

    return existing


def download_track_ids(tracks: list[dict], api: spotipy.Spotify) -> list[dict]:
    bar = Bar('Downloading track ids...', max=len(tracks))
    for track in tracks:
        bar.next()
        # Preserve original id for duplicate checking
        track['tt_id'] = track['id']

        response = api.search(q=track['title'], type='track')
        if response['tracks']['total'] == 0:
            track['id'] = None
            continue

        item = response['tracks']['items'][0]
        track['id'] = item['id']

        track['popularity'] = item['popularity']

    return tracks


def download_features(tracks: list[dict], api: spotipy.Spotify, chunk: int = 100) -> list[dict]:
    batch = []
    results = []

    bar = Bar('Downloading track features...', max=len(tracks))
    for i, track in enumerate(tracks):
        bar.next()

        if track['id'] is None:
            results.append(track)
            continue

        batch.append(track)

        # Download audio features per batch or when reaching the last track
        if len(batch) % chunk == 0 or i == len(tracks) - 1:
            ids = [item['id'] for item in batch]
            response = api.audio_features(ids)
            for idx, features in enumerate(response):
                item = batch[idx]

                if features is None:
                    results.append(item)
                    continue

                combined = {**item, **features}
                results.append(combined)

            batch = []

    return results


def run(input_file: str, output_file: str, chunk: int, limit: int = None):
    credentials = SpotifyClientCredentials(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
    )
    api = spotipy.Spotify(auth_manager=credentials)

    tracks = read_tracks(input_file, strict=True)
    existing_tracks = update_existing_tracks(output_file, tracks)
    existing_ids = [track['tt_id'] for track in existing_tracks]
    new_tracks = [track for track in tracks if track['id'] not in existing_ids]

    logging.info(f"{len(new_tracks)} new tracks found since last run")

    if limit is not None:
        new_tracks = new_tracks[:limit]

    new_tracks = download_track_ids(new_tracks, api)
    new_tracks = download_features(new_tracks, api, chunk)

    write_tracks(output_file, existing_tracks + new_tracks, overwrite=True)
