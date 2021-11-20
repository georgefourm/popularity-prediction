import os

from src.util import read_csv, write_csv
from progress.bar import Bar
import requests
import json


def download_tags(tracks: list[dict]):
    url = os.getenv("LASTFM_API_URL")
    api_key = os.getenv("LASTFM_API_KEY")
    common_params = {
        'api_key': api_key,
        'format': 'json',
    }

    results = []
    bar = Bar(message="Downloading tags", max=len(tracks))
    for track in tracks:
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
        results.append({
            'id': track['id'],
            'title': track_info['name'],
            'artist': track_info['artist'],
            'listeners': track_info['listeners'],
            'tags': json.dumps(tags)
        })
        bar.next()

    return results


def run(input_file: str, output_file: str, limit: int = None):
    tracks = read_csv(input_file, strict=True)

    existing_tags = read_csv(output_file)
    existing_ids = {tag['id'] for tag in existing_tags}
    tracks = [track for track in tracks if track['id'] not in existing_ids]

    if limit is not None:
        tracks = tracks[:limit]

    tags = download_tags(tracks)

    file_exists = os.path.exists(output_file)
    write_csv(output_file, tags, overwrite=not file_exists)
