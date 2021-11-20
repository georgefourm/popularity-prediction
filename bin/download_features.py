import logging
from argparse import ArgumentParser

from src.data.features import FeatureDownloader

if __name__ == "__main__":
    parser = ArgumentParser(description="Retrieve track audio features using the Spotify API")
    parser.add_argument(
        "-i", "--input",
        help="The file that contains the track view data",
        default="data/raw/tracks.csv"
    )
    parser.add_argument(
        "-o", "--output",
        help="The file that contains the track audio feature data",
        default="data/raw/features.csv"
    )
    parser.add_argument(
        "-c", "--chunk",
        help="The chunk size to write out.",
        default=100,
        type=int
    )
    parser.add_argument(
        "-l", "--limit",
        help="The maximum amount of data points to download",
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

    downloader = FeatureDownloader(args.output, args.input)
    downloader.run(
        chunk=args.chunk,
        limit=args.limit
    )
