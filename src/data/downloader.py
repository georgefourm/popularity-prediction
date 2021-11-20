import logging
import os.path
from typing import Iterator

from src.util import write_csv


class DataDownloader:
    def __init__(self, output_file: str):
        self.output_file = output_file

    def download(self) -> Iterator[dict]:
        pass

    def run(self, chunk: int = 100, limit: int = None):
        batch = []
        i = -1
        for i, datapoint in enumerate(self.download()):
            batch.append(datapoint)
            if (i + 1) % chunk == 0:
                self.write_chunk(batch)
                batch = []
            if limit is not None and i + 1 == limit:
                break

        if len(batch) > 0:
            self.write_chunk(batch)

        logging.info(f"Processed {i + 1} total data points")

    def write_chunk(self, chunk: list[dict]):
        exists = os.path.exists(self.output_file)
        write_csv(self.output_file, chunk, overwrite=not exists)
