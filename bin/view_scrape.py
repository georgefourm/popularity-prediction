from argparse import ArgumentParser
from dotenv import load_dotenv
import logging

from src.tiktok_scrape import run

if __name__ == "__main__":
    load_dotenv()

    parser = ArgumentParser(description="Retrieve track views data by scraping the TikTok API")
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

    run(
        file=args.file,
        chunk=args.chunk,
        wait=args.wait,
        threshold=args.threshold
    )
