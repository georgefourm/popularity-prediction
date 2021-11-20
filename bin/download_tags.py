import logging
from argparse import ArgumentParser

from src.data.tags import TagDownloader

if __name__ == "__main__":
    parser = ArgumentParser(description="Retrieve track tags using the LastFM API")
    parser.add_argument(
        "-i", "--input",
        help="The file that contains the track feature data",
        default="data/raw/features.csv"
    )
    parser.add_argument(
        "-o", "--output",
        help="The output file to store the tags",
        default="data/raw/tags.csv"
    )
    parser.add_argument(
        "-c", "--chunk",
        help="The chunk size to write out.",
        default=100,
        type=int
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

    downloader = TagDownloader(args.output, args.input)
    downloader.run(
        limit=args.limit,
        chunk=args.chunk
    )
