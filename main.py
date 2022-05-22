import argparse
import logging
import os.path
from pathlib import Path

from src.core import Downloader

log = logging.getLogger("main")


def main(output_dir: Path):
    Downloader(output_dir).run()


if __name__ == '__main__':
    output_default = f"{os.getcwd()}/wis_projects"

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", action="store", dest="output_dir", default=output_default)
    parser.add_argument("-v", action="count", dest="version", default=0)
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(name)s]: %(message)s",
        level=logging.WARNING - args.version * 10,
    )

    output_directory = Path(args.output_dir)
    main(output_directory)
