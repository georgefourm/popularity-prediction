import logging
import os
from csv import DictReader, DictWriter


def read_csv(input_file: str, strict=False) -> list[dict]:
    """
    Reads the data from a CSV file
    :param input_file: The file to read
    :param strict: Whether to throw an exception if the file is missing.
    If the file is missing and strict=False, an empty list will be returned
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


def write_csv(output_file: str, data: list[dict], overwrite=True):
    """
    Writes a list of data into a CSV file
    :param output_file: The file to write
    :param data: The list of dicts to write
    :param overwrite: Whether to overwrite the output file, or append to its end
    :return:
    """
    mode = 'w' if overwrite else 'a'
    with open(output_file, mode=mode, encoding='utf_8', newline='') as file:
        writer = DictWriter(file, fieldnames=list(data[0].keys()))
        if overwrite:
            writer.writeheader()
        writer.writerows(data)
