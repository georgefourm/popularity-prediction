import logging
import os
from csv import DictReader, DictWriter


def read_tracks(input_file: str, strict=False) -> list[dict]:
    """
    Reads the track data from a CSV file
    :param input_file: The file to read
    :param strict: Whether to throw an exception if the file is missing
    :return:
    """
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
    """
    Writes a list of tracks into a CSV file
    :param output_file: The file to write
    :param tracks: The list of tracks to write
    :param overwrite: Whether to overwrite the output file, or append to its end
    :return:
    """
    mode = 'w' if overwrite else 'a'
    with open(output_file, mode=mode, encoding='utf_8', newline='') as file:
        writer = DictWriter(file, fieldnames=list(tracks[0].keys()))
        if overwrite:
            writer.writeheader()
        writer.writerows(tracks)
