import logging
from argparse import ArgumentParser

from src.data.tracks import TracksDownloader

if __name__ == "__main__":
    parser = ArgumentParser(description="Retrieve track and views data by scraping the TikTok API")
    parser.add_argument(
        "-f", "--file",
        help="The file to write the tracks to",
        default="data/raw/tracks.csv"
    )
    parser.add_argument(
        "-c", "--chunk",
        help="The amount of videos to download each iteration",
        default=1000,
        type=int
    )
    parser.add_argument(
        "-l", "--limit",
        help="The maximum amount of total new data points to add. This may be slightly exceeded depending on chunk.",
        type=int
    )
    parser.add_argument(
        "-w", "--wait",
        help="How many seconds to wait between each iteration",
        default=10,
        type=int
    )
    parser.add_argument(
        "-t", "--threshold",
        help="How many new tracks should be added at minimum to continue the scraping",
        default=1,
        type=int
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Whether to enable verbose logging",
        action="store_true"
    )
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%I:%M:%S',
        level=logging.INFO if args.verbose else logging.WARN
    )

    downloader = TracksDownloader(args.file, threshold=args.threshold, wait=args.wait)
    downloader.run(
        chunk=args.chunk,
    )
