from argparse import ArgumentParser
from dotenv import load_dotenv
import logging

from src.spotify_scrape import run

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S', level=logging.INFO)

    parser = ArgumentParser(description="Retrieve track audio features using the Spotify API")
    parser.add_argument(
        "-i", "--input",
        help="The file that contains the track view data",
        default="data/raw/tracks.csv"
    )
    parser.add_argument(
        "-o", "--output",
        help="The file that contains the track audio feature data",
        default="data/interim/tracks.csv"
    )
    parser.add_argument(
        "-c", "--chunk",
        help="The batch size to download tracks (Spotify allows up to 100).",
        default=100,
        type=int
    )
    args = parser.parse_args()
    run(
        input_file=args.input,
        output_file=args.output,
        chunk=args.chunk
    )
