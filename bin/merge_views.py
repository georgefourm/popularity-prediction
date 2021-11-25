import logging
from argparse import ArgumentParser
from csv import DictReader

from src.util import read_csv, write_csv


def merge_file(source_file: str, target_file: str):
    """
    Merges the scrape results from two different files, updating existing track data if found
    :param source_file:
    :param target_file:
    :return:
    """
    existing = read_csv(source_file)
    existing = {track['id']: track for track in existing}
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

    write_csv(target_file, list(existing.values()), overwrite=True)
    logging.info(f"Added {added} new tracks, updated {updated} tracks")


if __name__ == "__main__":
    parser = ArgumentParser(description="Merge view data files")

    parser.add_argument(
        "source",
        help="The source file to merge",
        type=str
    )

    parser.add_argument(
        "target",
        help="The target file to merge into"
    )

    parser.add_argument(
        "-v", "--verbose",
        help="Whether to enable verbose logging",
        action="store_true",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%I:%M:%S',
        level=logging.INFO if args.verbose else logging.WARN
    )

    merge_file(args.source, args.target)
