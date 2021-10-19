import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from csv import DictReader, DictWriter
from progress.bar import Bar
import logging


def read_tracks(input_file: str):
    result = []
    with open(input_file, mode='r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            result.append(line)

    return result


def filter_new_tracks(output_file: str, tracks: list[dict]) -> list[dict]:
    existing = []
    if not os.path.isfile(output_file):
        return tracks

    with open(output_file, mode='r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            existing.append(line['tt_id'])
    filtered = filter(lambda item: item['id'] not in existing, tracks)

    return list(filtered)


def find_track_ids(tracks: list[dict], api: spotipy.Spotify, limit: int = None) -> dict[dict]:
    tracks_by_id = dict()

    bar = Bar('Downloading track ids...', max=len(tracks))
    for track in tracks:
        response = api.search(q=track['title'], type='track')
        if response['tracks']['total'] == 0:
            continue
        item = response['tracks']['items'][0]
        # Preserve original id
        track['tt_id'] = track['id']
        tracks_by_id[item['id']] = track
        bar.next()
        if limit is not None and bar.index == limit:
            break

    return tracks_by_id


def download_features(tracks_by_id: dict[dict], api: spotipy.Spotify, chunk: int = 100) -> list[dict]:
    ids = []
    counter = 0
    results = []
    total_written = 0

    bar = Bar('Downloading track features...', max=len(tracks_by_id))
    for track_id in tracks_by_id.keys():
        ids.append(track_id)
        counter += 1
        total_written += 1

        if counter % chunk == 0 or len(tracks_by_id) == total_written:
            response = api.audio_features(ids)
            for idx, features in enumerate(response):
                if features is None:
                    continue
                track = tracks_by_id[ids[idx]]
                combined = {**track, **features}
                results.append(combined)

            counter = 0
            ids = []
        bar.next()

    return results


def write_tracks(output_file: str, tracks: list[dict]):
    file_exists = os.path.isfile(output_file)
    mode = 'a' if file_exists else 'w'

    with open(output_file, mode=mode, encoding='utf_8', newline='') as file:
        writer = DictWriter(file, fieldnames=list(tracks[0].keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerows(tracks)


def run(input_file: str, output_file: str, chunk: int):
    load_dotenv()
    credentials = SpotifyClientCredentials(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
    )
    api = spotipy.Spotify(auth_manager=credentials)
    tracks = read_tracks(input_file)

    new_tracks = filter_new_tracks(output_file, tracks)
    logging.info(f"{len(new_tracks)} new tracks found since last run")

    tracks_by_id = find_track_ids(new_tracks, api)
    tracks_with_features = download_features(tracks_by_id, api, chunk)

    write_tracks(output_file, tracks_with_features)
