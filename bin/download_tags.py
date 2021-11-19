import logging
from argparse import ArgumentParser

from src.lastfm_scrape import run

if __name__ == "__main__":
    parser = ArgumentParser(description="Retrieve track tags using the LastFM API")
    parser.add_argument(
        "-i", "--input",
        help="The file that contains the track data",
        default="data/processed/tracks.csv"
    )
    parser.add_argument(
        "-o", "--output",
        help="The output file to store the tags",
        default="data/raw/tags.csv"
    )
    parser.add_argument(
        "-l", "--limit",
        help="The amount of track tags to download",
        type=int,
        default=None
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

    run(
        input_file=args.input,
        output_file=args.output,
        limit=args.limit
    )
