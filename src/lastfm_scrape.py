import os

from src.util import read_tracks, write_tracks
from progress.bar import Bar
import requests
import json


def download_tags(tracks: list[dict], limit: int = None, existing_tags=None):
    if existing_tags is None:
        existing_tags = []
    else:
        existing_tags = [tag['id'] for tag in existing_tags]

    url = os.getenv("LASTFM_API_URL")
    api_key = os.getenv("LASTFM_API_KEY")
    common_params = {
        'api_key': api_key,
        'format': 'json',
        'method': 'track.search'
    }

    results = []
    bar = Bar(message="Downloading tags", max=min(limit, len(tracks)))
    for track in tracks:
        if track['id'] in existing_tags:
            continue

        response = requests.get(url, params={**common_params, 'track': track['title']})
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

        if len(tag_info['toptags']['tag']) == 0:
            continue

        tags = tag_info['toptags']['tag']
        results.append({
            'id': track['id'],
            'title': track_info['name'],
            'artist': track_info['artist'],
            'listeners': track_info['listeners'],
            'tags': json.dumps(tags)
        })
        bar.next()

        if limit is not None and bar.index == limit:
            break

    return results


def run(input_file: str, output_file: str, limit: int = None):
    tracks = read_tracks(input_file, strict=True)
    existing_tags = read_tracks(output_file)
    tags = download_tags(tracks, limit, existing_tags)

    file_exists = os.path.exists(output_file)
    write_tracks(output_file, tags, overwrite=not file_exists)
