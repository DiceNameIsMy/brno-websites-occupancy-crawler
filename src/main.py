import argparse
import sys
import os

# Add the src directory to the python path so we can import crawlers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.luzanky import LuzankyCrawler
from crawlers.hangar import HangarCrawler


def main():
    parser = argparse.ArgumentParser(
        description="Crawler for pool and climbing gym occupancy."
    )
    parser.add_argument(
        "--source",
        choices=["luzanky", "hangar", "all"],
        default="all",
        help="Source to crawl (default: all)",
    )
    args = parser.parse_args()

    crawlers = []
    if args.source in ["luzanky", "all"]:
        crawlers.append(LuzankyCrawler())
    if args.source in ["hangar", "all"]:
        crawlers.append(HangarCrawler())

    for crawler in crawlers:
        print(f"Running crawler for {crawler.source_name}...")
        crawler.run()


if __name__ == "__main__":
    main()
