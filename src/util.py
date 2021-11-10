import logging
import os
from csv import DictReader, DictWriter


def read_tracks(input_file: str, strict=False) -> list:
    if not os.path.isfile(input_file) and not strict:
        logging.warning("File not found: " + input_file)
        return []

    result = []
    with open(input_file, mode='r', encoding='utf_8', newline='') as file:
        reader = DictReader(file)
        for line in reader:
            result.append(line)

    return result


def write_tracks(output_file: str, tracks: list[dict], overwrite=True):
    mode = 'w' if overwrite else 'a'
    with open(output_file, mode=mode, encoding='utf_8', newline='') as file:
        writer = DictWriter(file, fieldnames=list(tracks[0].keys()))
        if overwrite:
            writer.writeheader()
        writer.writerows(tracks)
